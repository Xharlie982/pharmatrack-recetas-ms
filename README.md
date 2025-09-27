# PharmaTrack – Recetas & Dispensación

FastAPI + MySQL. Valida `id_producto` contra el microservicio **Catálogo**.

**Cómo correr**
1) Copia `.env.example` a `.env`  
2) `docker compose up -d --build`  
3) Swagger: http://localhost:8081/docs

**.env (ejemplo)**
- `MYSQL_URL=mysql+pymysql://user:pass@mysql:3306/recetas?charset=utf8mb4`
- `CATALOGO_BASE_URL=http://3.219.80.35:8083`

**Endpoints**
- `GET /health`
- `POST /recetas`
- `GET /recetas/{id}`
- `POST /dispensaciones`

**Ejemplos rápidos (curl)**
- Crear receta: `curl -X POST http://localhost:8081/recetas -H "Content-Type: application/json" -d '{"id_sucursal":101,"detalles":[{"id_producto":"P123","cantidad":2}]}'`
- Crear dispensación: `curl -X POST http://localhost:8081/dispensaciones -H "Content-Type: application/json" -d '{"id_receta":1,"detalles":[{"id_producto":"P123","cantidad_dispensada":2}]}'`
