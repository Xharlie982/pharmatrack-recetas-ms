CREATE DATABASE IF NOT EXISTS recetas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE recetas;

CREATE TABLE IF NOT EXISTS receta (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  id_sucursal INT NOT NULL,
  fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  estado ENUM('pendiente','parcial','completa') NOT NULL DEFAULT 'pendiente',
  INDEX (id_sucursal),
  INDEX (estado),
  INDEX (fecha)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS receta_detalle (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  id_receta BIGINT NOT NULL,
  id_producto VARCHAR(64) NOT NULL,
  cantidad INT NOT NULL,
  CONSTRAINT fk_receta_detalle_receta
    FOREIGN KEY (id_receta) REFERENCES receta(id)
    ON DELETE CASCADE,
  INDEX (id_receta),
  INDEX (id_producto)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dispensacion (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  id_receta BIGINT NOT NULL,
  fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_dispensacion_receta
    FOREIGN KEY (id_receta) REFERENCES receta(id)
    ON DELETE CASCADE,
  INDEX (id_receta),
  INDEX (fecha)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dispensacion_detalle (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  id_dispensacion BIGINT NOT NULL,
  id_producto VARCHAR(64) NOT NULL,
  cantidad_dispensada INT NOT NULL,
  CONSTRAINT fk_disp_det_disp
    FOREIGN KEY (id_dispensacion) REFERENCES dispensacion(id)
    ON DELETE CASCADE,
  INDEX (id_dispensacion),
  INDEX (id_producto)
) ENGINE=InnoDB;
