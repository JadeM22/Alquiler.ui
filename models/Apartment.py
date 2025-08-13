from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import Optional
import re

class Apartment(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente desde el _id de MongoDB"
    )

    number: str = Field(
        description="Numero del apartamento",
        min_length=1,
        max_length=10,
        examples=["A123", "B205"]
    )

    level: str = Field(
        description="Numero de nivel del edificio",
        min_length=1,
        max_length=10,
        examples=["A1", "2"]
    )

    active: bool = Field(
        default=True,
        description="Estado activo del apartamento"
    )

    
