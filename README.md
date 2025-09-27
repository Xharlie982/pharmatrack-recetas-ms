# PharmaTrack - Recetas & Dispensación (FastAPI + MySQL)

## Desarrollo local
\\\ash
docker compose down
docker compose up -d --build
\\\

Abrir: http://localhost:8081/docs

## Variables (.env)
- **MYSQL_URL**: \mysql+pymysql://user:pass@mysql:3306/recetas?charset=utf8mb4\
- **CATALOGO_BASE_URL**: \http://3.219.80.35:8083\

> En producción, apunta **MYSQL_URL** a tu RDS/VM de MySQL y **CATALOGO_BASE_URL** al dominio/IP del microservicio "Catálogo" real.
