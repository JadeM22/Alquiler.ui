from fastapi import APIRouter, HTTPException, Request
from models.Apartment import Apartment
from controllers.Apartment import (
    create_Apartment,
    get_Apartment,
    get_Apartment_id,
    update_Apartment,
    deactivate_Apartment
)
from utils.security import validateadmin

router = APIRouter()

# Crear un nuevo apartamento (solo administradores)
@router.post("/apartments", response_model=Apartment, tags=["🏢 Apartments"])
@validateadmin   
async def create_apartment_endpoint(request: Request, apartment: Apartment) -> Apartment:
    """
    Crear un nuevo apartamento (solo administradores).
    """
    return await create_Apartment(apartment)


# Obtener todos los apartamentos (público)
@router.get("/apartments", response_model=list[Apartment], tags=["🏢 Apartments"])
async def get_apartments_endpoint() -> list[Apartment]:
    """Obtener todos los apartamentos"""
    return await get_Apartment()


# Obtener un apartamento por ID (público)
@router.get("/apartments/{apartment_id}", response_model=Apartment, tags=["🏢 Apartments"])
async def get_apartment_by_id_endpoint(apartment_id: str) -> Apartment:
    """Obtener un apartamento por ID"""
    return await get_Apartment_id(apartment_id)


# Actualizar un apartamento (solo administradores)
@router.put("/apartments/{apartment_id}", response_model=Apartment, tags=["🏢 Apartments"])
@validateadmin   
async def update_apartment_endpoint(request: Request, apartment_id: str, apartment: Apartment) -> Apartment:
    """Actualizar un apartamento (solo administradores)"""
    return await update_Apartment(apartment_id, apartment)


# Desactivar un apartamento (solo administradores)
@router.delete("/apartments/{apartment_id}", response_model=Apartment, tags=["🏢 Apartments"])
@validateadmin   
async def deactivate_apartment_endpoint(request: Request, apartment_id: str) -> Apartment:
    """Desactivar un apartamento (solo administradores)"""
    return await deactivate_Apartment(apartment_id)
