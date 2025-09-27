from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, select
from .db import get_db, engine
from . import models, schemas, crud
from .config import settings
import httpx, time

app = FastAPI(title="Microservicio Recetas & Dispensación", version="1.2.2")

@app.get("/health")
def health():
    return {"ok": True}

def wait_for_db(max_wait_s: int = 60):
    start = time.time()
    while True:
        try:
            with engine.connect() as cx:
                cx.execute(text("SELECT 1"))
            return
        except Exception:
            if time.time() - start > max_wait_s:
                raise
            time.sleep(2)

# Esperar DB y crear tablas (dev/primera vez)
try:
    wait_for_db()
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print("DB init skipped/error:", e)

async def validar_ids_en_catalogo(ids: list[str]) -> None:
    unicos = sorted(set(ids))
    async with httpx.AsyncClient(timeout=5.0) as cli:
        for pid in unicos:
            try:
                # GET {CATALOGO_BASE_URL}/productos/{id}
                r = await cli.get(f"{settings.CATALOGO_BASE_URL}/productos/{pid}")
            except httpx.RequestError:
                raise HTTPException(status_code=503, detail="Catálogo no disponible")
            if r.status_code == 404:
                raise HTTPException(status_code=400, detail=f"Producto {pid} no existe en catálogo")
            if r.status_code >= 400:
                raise HTTPException(status_code=503, detail="Error consultando Catálogo")

@app.post("/recetas", response_model=schemas.RecetaOut, status_code=201)
async def crear_receta(payload: schemas.RecetaCreate, db: Session = Depends(get_db)):
    if not payload.detalles:
        raise HTTPException(400, "La receta debe tener al menos un detalle.")
    await validar_ids_en_catalogo([d.id_producto for d in payload.detalles])

    try:
        receta = crud.crear_receta(db, payload)
        db.commit()
        db.refresh(receta)
    except Exception as e:
        db.rollback()
        print("Error al crear receta:", repr(e))
        raise HTTPException(500, "Error interno creando la receta")

    receta = crud.get_receta_completa(db, receta.id)
    return receta

@app.get("/recetas/{receta_id}", response_model=schemas.RecetaOut)
def obtener_receta(receta_id: int, db: Session = Depends(get_db)):
    receta = crud.get_receta_completa(db, receta_id)
    if not receta:
        raise HTTPException(404, "Receta no encontrada")
    return receta

@app.post("/dispensaciones", response_model=schemas.DispensacionOut, status_code=201)
async def crear_dispensacion(payload: schemas.DispensacionCreate, db: Session = Depends(get_db)):
    receta = db.get(models.Receta, payload.id_receta)
    if not receta:
        raise HTTPException(404, "Receta no existe")
    if not payload.detalles:
        raise HTTPException(400, "Debe enviar al menos un detalle de dispensación.")

    # Validar catálogo
    ids_en_dispensacion = {d.id_producto for d in payload.detalles}
    await validar_ids_en_catalogo(list(ids_en_dispensacion))

    # Productos permitidos de la receta SIN lazy-load
    permitidos = db.execute(
        select(models.RecetaDetalle.id_producto).where(models.RecetaDetalle.id_receta == payload.id_receta)
    ).scalars().all()
    ids_permitidos = set(permitidos)

    faltantes = ids_en_dispensacion - ids_permitidos
    if faltantes:
        raise HTTPException(400, detail=f"Productos no incluidos en la receta: {sorted(faltantes)}")

    try:
        disp = crud.crear_dispensacion(db, payload)
        db.commit()
        db.refresh(disp)
        return disp
    except Exception as e:
        db.rollback()
        print("Error al crear dispensación:", repr(e))
        raise HTTPException(500, "Error interno creando la dispensación")
