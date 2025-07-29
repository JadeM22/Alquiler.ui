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

    photo_url: Optional[str] = Field(
        description="URL de la foto del apartamento",
        examples=["https://mi-sitio.com/fotos/apartamento1.jpg"]
    )

    active: bool = Field(
        default=True,
        description="Estado activo del apartamento"
    )

    @field_validator("photo_url")
    def validate_url(cls, v):
        if v is None:
            return v
        regex = re.compile(
            r"^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$"
        )
        if not regex.match(v):
            raise ValueError("URL no válida")
        return v
