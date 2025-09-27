from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="PharmaTrack - Catálogo (mock)", version="1.0.0")

class ProductoIn(BaseModel):
    id: str
    nombre: str
    presentacion: str | None = None

# almacenamiento en memoria
PRODUCTOS: dict[str, dict] = {
    "P123": {"id": "P123", "nombre": "Paracetamol 500mg", "presentacion": "tabletas"},
    "P150": {"id": "P150", "nombre": "Ibuprofeno 400mg", "presentacion": "capsulas"},
}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/productos/{id}")
def get_producto(id: str):
    if id in PRODUCTOS:
        return PRODUCTOS[id]
    raise HTTPException(status_code=404, detail="No encontrado")

@app.post("/productos", status_code=201)
def crear_producto(p: ProductoIn):
    PRODUCTOS[p.id] = p.model_dump()
    return p

@app.post("/productos:bulk", status_code=201)
def bulk(productos: list[ProductoIn]):
    for p in productos:
        PRODUCTOS[p.id] = p.model_dump()
    return {"insertados": len(productos)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8083)
