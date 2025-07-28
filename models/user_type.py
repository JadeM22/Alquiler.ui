from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class User_Type(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente desde el _id de MongoDB"
    )

    description: str = Field(
        description="Descripción del tipo de usuario",
        pattern=r"^[A-Za-zÁÉÍÓÚÑáéíóúñ -]+$",
        examples=["user", "aadmin"]
    )
