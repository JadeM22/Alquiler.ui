from fastapi import APIRouter, HTTPException, Request, Query
from models.Apartment import Apartment
from controllers.Apartment import (
    create_Apartment,
    get_Apartment,
    get_Apartment_id,
    update_Apartment,
    deactivate_Apartment
)
from utils.security import validateuser

router = APIRouter()

# -----------------------
# Crear un nuevo apartamento (solo administradores)
# -----------------------
@router.post("/apartments", response_model=Apartment, tags=["🏢 Apartments"])
@validateuser 
async def create_apartment_endpoint(request: Request, apartment: Apartment) -> Apartment:
    return await create_Apartment(apartment)


# -----------------------
# Obtener todos los apartamentos (publico)
# -----------------------
@router.get("/apartments", response_model=list[Apartment], tags=["🏢 Apartments"])
async def get_apartments_endpoint() -> list[Apartment]:
    return await get_Apartment()


# -----------------------
# Obtener un apartamento por ID (público)
# -----------------------
@router.get("/apartments/{apartment_id}", response_model=Apartment, tags=["🏢 Apartments"])
async def get_apartment_by_id_endpoint(apartment_id: str) -> Apartment:
    return await get_Apartment_id(apartment_id)


# -----------------------
# Actualizar un apartamento (solo administradores)
# -----------------------
@router.put("/apartments/{apartment_id}", response_model=Apartment, tags=["🏢 Apartments"])
@validateuser 
async def update_apartment_endpoint(request: Request, apartment_id: str, apartment: Apartment) -> Apartment:
    return await update_Apartment(apartment_id, apartment)


# -----------------------
# Desactivar o eliminar un apartamento (solo administradores)
# -----------------------
@router.delete("/apartments/{apartment_id}", tags=["🏢 Apartments"])
@validateuser 
async def deactivate_apartment_endpoint(request: Request, apartment_id: str) -> dict:
    """
    Si el apartamento tiene contratos, cambia su status a 'inactive'.
    Si no tiene contratos, lo elimina.
    """
    return await deactivate_Apartment(apartment_id)
