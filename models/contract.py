from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date

class Contract(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente desde el _id de MongoDB"
    )

    id_User: str = Field(
        description="ID del usuario",
        examples=["507f1f77bcf86cd799439012"]
    )

    id_Aparment: str = Field(
        description="ID del Apartamento",
        examples=["507f1f77bcf86cd799439012"]
    )

    start_date: date = Field(
        description="Fecha de inicio del contrato",
        examples=["2025-07-01"]
    )

    end_date: date = Field(
        description="Fecha de finalización del contrato",
        examples=["2026-07-01"]
    )
    
    active: bool = Field(
        default=True,
        description="Estado activo del contrato"
    )