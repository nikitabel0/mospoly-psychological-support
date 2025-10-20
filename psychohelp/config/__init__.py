import os

__all__ = ["SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE"]

SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE", 30))
