from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from .models import EstadoReceta

# Receta
class RecetaDetalleIn(BaseModel):
    id_producto: str
    cantidad: int = Field(gt=0)

class RecetaCreate(BaseModel):
    id_sucursal: int
    detalles: List[RecetaDetalleIn]

class RecetaDetalleOut(RecetaDetalleIn):
    id: int

class RecetaOut(BaseModel):
    id: int
    id_sucursal: int
    fecha: datetime
    estado: EstadoReceta
    detalles: List[RecetaDetalleOut]
    class Config:
        from_attributes = True

# Dispensación
class DispDetalleIn(BaseModel):
    id_producto: str
    cantidad_dispensada: int = Field(gt=0)

class DispensacionCreate(BaseModel):
    id_receta: int
    detalles: List[DispDetalleIn]

class DispDetalleOut(DispDetalleIn):
    id: int

class DispensacionOut(BaseModel):
    id: int
    id_receta: int
    fecha: datetime
    detalles: List[DispDetalleOut]
    class Config:
        from_attributes = True
