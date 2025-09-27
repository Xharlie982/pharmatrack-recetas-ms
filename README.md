# PharmaTrack - Recetas & Dispensación (FastAPI + MySQL)

## Desarrollo local
docker compose up -d --build
Abrir: http://localhost:8081/docs

## Variables (.env)
MYSQL_URL=mysql+pymysql://user:pass@mysql:3306/recetas?charset=utf8mb4
CATALOGO_BASE_URL=http://catalogo_mock:8083
