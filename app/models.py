from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, Enum, DateTime, ForeignKey, func
import enum

class Base(DeclarativeBase):
    pass

class EstadoReceta(str, enum.Enum):
    pendiente = "pendiente"
    parcial   = "parcial"
    completa  = "completa"

class Receta(Base):
    __tablename__ = "receta"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_sucursal: Mapped[int] = mapped_column()
    fecha: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now())
    estado: Mapped[EstadoReceta] = mapped_column(Enum(EstadoReceta), default=EstadoReceta.pendiente)

    detalles: Mapped[list["RecetaDetalle"]] = relationship(back_populates="receta", cascade="all, delete-orphan")
    dispensaciones: Mapped[list["Dispensacion"]] = relationship(back_populates="receta", cascade="all, delete-orphan")

class RecetaDetalle(Base):
    __tablename__ = "receta_detalle"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_receta: Mapped[int] = mapped_column(ForeignKey("receta.id", ondelete="CASCADE"), index=True)
    id_producto: Mapped[str] = mapped_column(String(64), index=True)
    cantidad: Mapped[int] = mapped_column(Integer)
    receta: Mapped[Receta] = relationship(back_populates="detalles")

class Dispensacion(Base):
    __tablename__ = "dispensacion"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_receta: Mapped[int] = mapped_column(ForeignKey("receta.id", ondelete="CASCADE"), index=True)
    fecha: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now())
    receta: Mapped[Receta] = relationship(back_populates="dispensaciones")
    detalles: Mapped[list["DispensacionDetalle"]] = relationship(back_populates="dispensacion", cascade="all, delete-orphan")

class DispensacionDetalle(Base):
    __tablename__ = "dispensacion_detalle"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_dispensacion: Mapped[int] = mapped_column(ForeignKey("dispensacion.id", ondelete="CASCADE"), index=True)
    id_producto: Mapped[str] = mapped_column(String(64), index=True)
    cantidad_dispensada: Mapped[int] = mapped_column(Integer)
    dispensacion: Mapped[Dispensacion] = relationship(back_populates="detalles")
