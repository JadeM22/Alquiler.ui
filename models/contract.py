from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class Contract(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID generado automáticamente desde _id"
    )

    id_User: str = Field(
        description="ID del usuario dueño del contrato",
        examples=["507f1f77bcf86cd799439012"]
    )

    id_Apartment: str = Field(
        description="ID del apartamento asociado",
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
        description="Indica si el contrato está activo"
    )
