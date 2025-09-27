# PharmaTrack – Recetas y Dispensación
---
## 1) Instalar Docker y preparar datos

```bash
sudo apt-get update -y
sudo apt-get install -y docker.io docker-compose-plugin
sudo mkdir -p /opt/mysql
```

---

## 2) Crear migración inicial (V1)

```bash
mkdir -p ~/pharmatrack-recetas-ms/migrations
cat > ~/pharmatrack-recetas-ms/migrations/V1__init.sql <<'SQL'
CREATE DATABASE IF NOT EXISTS recetas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE recetas;

CREATE TABLE IF NOT EXISTS receta (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  id_sucursal INT NOT NULL,
  fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  estado ENUM('pendiente','parcial','completa') NOT NULL DEFAULT 'pendiente',
  INDEX (id_sucursal), INDEX (estado), INDEX (fecha)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS receta_detalle (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  id_receta BIGINT NOT NULL,
  id_producto VARCHAR(64) NOT NULL,
  cantidad INT NOT NULL,
  CONSTRAINT fk_receta_detalle_receta FOREIGN KEY (id_receta) REFERENCES receta(id) ON DELETE CASCADE,
  INDEX (id_receta), INDEX (id_producto)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dispensacion (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  id_receta BIGINT NOT NULL,
  fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_dispensacion_receta FOREIGN KEY (id_receta) REFERENCES receta(id) ON DELETE CASCADE,
  INDEX (id_receta), INDEX (fecha)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dispensacion_detalle (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  id_dispensacion BIGINT NOT NULL,
  id_producto VARCHAR(64) NOT NULL,
  cantidad_dispensada INT NOT NULL,
  CONSTRAINT fk_disp_det_disp FOREIGN KEY (id_dispensacion) REFERENCES dispensacion(id) ON DELETE CASCADE,
  INDEX (id_dispensacion), INDEX (id_producto)
) ENGINE=InnoDB;
SQL
```

---

## 3) Crear `docker-compose.db.yml`

```bash
cat > ~/pharmatrack-recetas-ms/docker-compose.db.yml <<'YAML'
services:
  mysql:
    image: mysql:8.0
    container_name: mysql
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: RootPass123!
      MYSQL_DATABASE: recetas
      MYSQL_USER: appuser
      MYSQL_PASSWORD: apppass
    volumes:
      - /opt/mysql:/var/lib/mysql
    restart: unless-stopped
    command:
      - "--character-set-server=utf8mb4"
      - "--collation-server=utf8mb4_unicode_ci"

  flyway:
    image: flyway/flyway:10
    container_name: flyway
    depends_on:
      - mysql
    command: >
      -url=jdbc:mysql://mysql:3306/recetas?allowPublicKeyRetrieval=true&useSSL=false
      -user=root
      -password=RootPass123!
      -connectRetries=60
      -locations=filesystem:/flyway/sql
      -mixed=true
      migrate
    volumes:
      - ./migrations:/flyway/sql:ro
YAML
```

---

## 4) Levantar MySQL y aplicar esquema

```bash
cd ~/pharmatrack-recetas-ms

# (si el puerto 3306 lo ocupa MySQL del host)
sudo systemctl stop mysql || true
sudo systemctl disable mysql || true

# Levantar MySQL
sudo docker compose -f docker-compose.db.yml up -d mysql

# (opcional) ver logs hasta "ready for connections"
sudo docker logs --tail=80 mysql

# Ejecutar migración V1
sudo docker compose -f docker-compose.db.yml up --no-deps flyway
```

---

## 5) Verificar

```bash
# Tablas
sudo docker exec -it mysql \
  mysql -uroot -pRootPass123! -e "SHOW TABLES FROM recetas;"

# Historial de Flyway
sudo docker exec -it mysql \
  mysql -uroot -pRootPass123! -e "SELECT version, description, success FROM recetas.flyway_schema_history;"
```

Listo. Con eso tu **BD queda arriba** en `3306` y con **todas las tablas creadas**.
