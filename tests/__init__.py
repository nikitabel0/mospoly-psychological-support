import httpx


def client():
    return httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True)
