from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class Pyment_Method(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente desde el _id de MongoDB"
    )

    description: str = Field(
        description="Descripción del metodo de pago",
        pattern=r"^[A-Za-zÁÉÍÓÚÑáéíóúñ -]+$",
        examples=["Transferencia", "Efectivo" , "Deposito"]
    )

    active: bool = Field(
        default=True,
        description="Estado activo del metodo de pago"
    )