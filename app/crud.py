from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func
import enum
from . import models, schemas

def crear_receta(db: Session, data: schemas.RecetaCreate) -> models.Receta:
    receta = models.Receta(id_sucursal=data.id_sucursal)
    receta.detalles = [
        models.RecetaDetalle(id_producto=d.id_producto, cantidad=d.cantidad)
        for d in data.detalles
    ]
    db.add(receta)
    db.flush()  # asegura receta.id
    return receta

def get_receta_completa(db: Session, receta_id: int) -> models.Receta | None:
    return (
        db.query(models.Receta)
        .options(joinedload(models.Receta.detalles))
        .filter(models.Receta.id == receta_id)
        .first()
    )

def crear_dispensacion(db: Session, data: schemas.DispensacionCreate) -> models.Dispensacion:
    # Cabecera
    disp = models.Dispensacion(id_receta=data.id_receta)
    db.add(disp)
    db.flush()  # disp.id

    # Detalles
    disp.detalles = [
        models.DispensacionDetalle(
            id_dispensacion=disp.id,
            id_producto=d.id_producto,
            cantidad_dispensada=d.cantidad_dispensada,
        )
        for d in data.detalles
    ]
    db.flush()

    # Requerido por receta
    req_rows = db.execute(
        select(
            models.RecetaDetalle.id_producto,
            func.coalesce(func.sum(models.RecetaDetalle.cantidad), 0),
        )
        .where(models.RecetaDetalle.id_receta == data.id_receta)
        .group_by(models.RecetaDetalle.id_producto)
    ).all()
    req = {row[0]: (row[1] or 0) for row in req_rows}

    # Entregado acumulado en todas las dispensaciones de esa receta (incluida esta)
    disp_rows = db.execute(
        select(
            models.DispensacionDetalle.id_producto,
            func.coalesce(func.sum(models.DispensacionDetalle.cantidad_dispensada), 0),
        )
        .join(
            models.Dispensacion,
            models.DispensacionDetalle.id_dispensacion == models.Dispensacion.id,
        )
        .where(models.Dispensacion.id_receta == data.id_receta)
        .group_by(models.DispensacionDetalle.id_producto)
    ).all()
    disp_acum = {row[0]: (row[1] or 0) for row in disp_rows}

    # Estado nuevo
    completa = True
    entregado_alguno = False
    for prod, cant_req in req.items():
        entregado = disp_acum.get(prod, 0)
        if entregado > 0:
            entregado_alguno = True
        if entregado < cant_req:
            completa = False

    nuevo_estado = (
        models.EstadoReceta.completa if completa
        else (models.EstadoReceta.parcial if entregado_alguno else models.EstadoReceta.pendiente)
    )

    # Si la columna es String, guarda el valor del Enum
    if isinstance(nuevo_estado, enum.Enum):
        nuevo_estado = nuevo_estado.value

    receta = db.get(models.Receta, data.id_receta)
    receta.estado = nuevo_estado
    db.flush()

    return disp
