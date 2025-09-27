import os

class Settings:
    MYSQL_URL: str = os.getenv(
        "MYSQL_URL",
        "mysql+pymysql://user:pass@mysql:3306/recetas?charset=utf8mb4"
    )
    CATALOGO_BASE_URL: str = os.getenv(
        "CATALOGO_BASE_URL",
        "http://catalogo:3000"  # ajusta host/puerto según tu entorno
    )

settings = Settings()
