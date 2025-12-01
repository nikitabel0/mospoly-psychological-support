import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient

from psychohelp.main import app


@pytest.fixture
def test_image_dir(monkeypatch):
    """Создать временную директорию с тестовыми изображениями"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # создаем тестовое изображение
        test_image = Path(tmpdir) / "test.jpg"
        test_image.write_bytes(b"fake image content")
        
        # создаем файл вне директории для теста
        parent_dir = Path(tmpdir).parent
        malicious_file = parent_dir / "secret.txt"
        malicious_file.write_text("secret data")
        
        # используем monkeypatch для изменения IMAGE_DIR в модуле
        import psychohelp.routes.controllers.images as images_module
        monkeypatch.setattr(images_module, "IMAGE_DIR", tmpdir)
        
        yield tmpdir
        
        # удаляем тестовый файл
        if malicious_file.exists():
            malicious_file.unlink()


class TestImagesPathTraversal:
    """Тесты для проверки защиты от Path Traversal атак"""
    
    def test_valid_image_access(self, test_image_dir):
        """Тест: легитимный доступ к изображению должен работать"""
        with TestClient(app) as client:
            r = client.get("/image/test.jpg")
            assert r.status_code == 200
            assert r.content == b"fake image content"
    
    def test_path_traversal_with_dots(self):
        """Тест: попытка path traversal с .. должна быть заблокирована"""
        with TestClient(app) as client:
            # различные варианты атак с ..
            # примечание: FastAPI/Starlette автоматически нормализует пути,
            # но наша защита на уровне имени файла все равно работает
            attacks = [
                "../../../etc/passwd",
                "../../secret.txt",
                "../secret.txt",
                "test/../../../etc/passwd",
            ]
            
            for attack in attacks:
                r = client.get(f"/image/{attack}")
                # FastAPI нормализует путь, поэтому мы получаем 404 или 400
                assert r.status_code in [400, 404], f"Attack '{attack}' was not properly handled (got {r.status_code})"
    
    def test_path_traversal_with_slash(self):
        """Тест: попытка использования абсолютных путей должна быть заблокирована"""
        with TestClient(app) as client:
            attacks = [
                "/etc/passwd",
                "/var/log/syslog",
                "\\etc\\passwd",  # windows style
                "/usr/local/secret.txt",
            ]
            
            for attack in attacks:
                r = client.get(f"/image/{attack}")
                # наша защита проверяет наличие / и \ в имени файла
                # FastAPI может нормализовать путь, но мы все равно блокируем
                assert r.status_code in [400, 404], f"Attack '{attack}' was not properly handled (got {r.status_code})"
    
    def test_invalid_file_extension(self):
        """Тест: файлы с недопустимыми расширениями должны блокироваться"""
        with TestClient(app) as client:
            invalid_files = [
                "malicious.php",
                "script.js",
                "config.conf",
                "data.txt",
                "app.py",
                "shell.sh",
                "executable.exe",
            ]
            
            for filename in invalid_files:
                r = client.get(f"/image/{filename}")
                assert r.status_code == 400, f"File '{filename}' was not blocked"
                assert "Недопустимый тип файла" in r.json()["detail"]
    
    def test_valid_image_extensions(self):
        """Тест: все допустимые расширения изображений"""
        # этот тест проверяет, что разрешенные расширения не блокируются
        # (файлы не существуют, поэтому будет 404, а не 400)
        with TestClient(app) as client:
            valid_extensions = [
                "photo.jpg",
                "photo.jpeg",
                "image.png",
                "animation.gif",
                "modern.webp",
                "vector.svg",
                "bitmap.bmp",
                "favicon.ico",
            ]
            
            for filename in valid_extensions:
                r = client.get(f"/image/{filename}")
                # должен быть 404 (файл не найден), а не 400 (недопустимый тип)
                assert r.status_code == 404, f"Valid extension '{filename}' was blocked"
    
    def test_nonexistent_file(self):
        """Тест: несуществующий файл должен возвращать 404"""
        with TestClient(app) as client:
            r = client.get("/image/nonexistent.jpg")
            assert r.status_code == 404
            assert "Файл не найден" in r.json()["detail"]
    
    def test_double_extension_bypass_attempt(self):
        """Тест: попытка обхода через двойное расширение"""
        with TestClient(app) as client:
            # попытка обмануть систему двойным расширением
            r = client.get("/image/malicious.php.jpg")
            # должно пройти проверку расширения (заканчивается на .jpg)
            # но вернуть 404 так как файла нет
            assert r.status_code == 404
    
    def test_null_byte_injection(self):
        """Тест: попытка инъекции null byte"""
        with TestClient(app) as client:
            # попытка использовать null byte для обхода проверки расширения
            attacks = [
                "malicious.php%00.jpg",
                "secret.txt%00.png",
            ]
            
            for attack in attacks:
                r = client.get(f"/image/{attack}")
                # должна быть заблокирована или файл не найден
                assert r.status_code in [400, 404]


class TestImagesSecurityHeaders:
    """Тесты для проверки правильной настройки заголовков безопасности"""
    
    def test_correct_content_type(self, test_image_dir):
        """Тест: проверка правильного Content-Type для изображений"""
        with TestClient(app) as client:
            # создаем реальный PNG файл
            png_path = Path(test_image_dir) / "real.png"
            # минимальный валидный PNG заголовок
            png_path.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
            
            r = client.get("/image/real.png")
            assert r.status_code == 200
            assert "image/" in r.headers.get("content-type", "").lower()


class TestImagesEdgeCases:
    """Тесты для граничных случаев"""
    
    def test_empty_filename(self):
        """Тест: пустое имя файла"""
        with TestClient(app) as client:
            r = client.get("/image/")
            # FastAPI может обработать это по-разному
            assert r.status_code in [404, 405]
    
    def test_filename_with_spaces(self):
        """Тест: имя файла с пробелами"""
        with TestClient(app) as client:
            r = client.get("/image/my%20photo.jpg")
            # должно быть 404 (файл не существует), не 400
            assert r.status_code == 404
    
    def test_case_sensitivity(self):
        """Тест: проверка регистронезависимости расширений"""
        with TestClient(app) as client:
            # расширения должны проверяться без учета регистра
            filenames = ["IMAGE.JPG", "Photo.PNG", "test.GIF"]
            
            for filename in filenames:
                r = client.get(f"/image/{filename}")
                # должен быть 404, а не 400 (расширение валидно)
                assert r.status_code == 404

