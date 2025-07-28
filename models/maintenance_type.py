from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class Maintenance_Type(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente desde el _id de MongoDB"
    )

    description: str = Field(
        description="Descripción del tipo de mantenimiento",
        pattern=r"^[A-Za-zÁÉÍÓÚÑáéíóúñ -]+$",
        examples=["Electrico", "Fontaneria" , "Carpinteria/Cerraduras" , "Pintura" , "Limpieza"]
    )

    base_cost: float = Field(
        description="Costo del tipo de mantenimiento",
        gt=0,
        examples=[150.50, 89.99]
    )

    active: bool = Field(
        default=True,
        description="Estado activo del tipo de mantenimiento"
    )