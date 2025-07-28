from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re
from datetime import datetime

class Pay(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente desde el _id de MongoDB"
    )

    id_Contract: str = Field(
        description="ID del conttrato",
        examples=["507f1f77bcf86cd799439012"]
    )

    cost: float = Field(
        description="Costo del pago",
        gt=0,
        examples=[150.50, 89.99]
    )

    date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha del pago"
    )

    id_Pyment_Method: str = Field(
        description="ID del metodo de pago",
        examples=["507f1f77bcf86cd799439012"]
    )
    
    is_paid: bool = Field(
        default=True,
        description="esta pagado o no "
    )

