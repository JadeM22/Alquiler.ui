from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Maintenance(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente desde el _id de MongoDB"
    )

    id_Apartment: str = Field(
        description="ID del Apartamento",
        examples=["507f1f77bcf86cd799439012"]
    )

    id_Contract: str = Field(
        description="ID del contrato",
        examples=["507f1f77bcf86cd799439012"]
    )

    id_Maintenance_type: str = Field(
        description="ID del tipo de mantenimiento",
        examples=["507f1f77bcf86cd799439012"]
    )

    cost: float = Field(
        description="Costo del mantenimiento. Se inicializa con el costo base del tipo de mantenimiento, pero puede modificarse.",
        gt=0,
        examples=[150.50, 200.00]
    )

    date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha del mantenimiento"
    )
