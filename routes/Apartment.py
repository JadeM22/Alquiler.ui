from fastapi import APIRouter, HTTPException, Request, Query, Body
from models.Apartment import Apartment
from controllers.Apartment import (
    create_Apartment,
    get_Apartment,
    get_Apartment_id,
    update_Apartment,
    delete_or_deactivate_apartment,
    toggle_apartment_status
)
from utils.security import validateuser

router = APIRouter()

# Crear un nuevo apartamento 
@router.post("/apartments", response_model=Apartment, tags=["🏢 Apartments"])
@validateuser 
async def create_apartment_endpoint(request: Request, apartment: Apartment) -> Apartment:
    return await create_Apartment(apartment)


# Obtener todos los apartamentos
@router.get("/apartments", response_model=list[Apartment], tags=["🏢 Apartments"])
async def get_apartments_endpoint() -> list[Apartment]:
    return await get_Apartment()


# Obtener un apartamento por ID 
@router.get("/apartments/{apartment_id}", response_model=Apartment, tags=["🏢 Apartments"])
async def get_apartment_by_id_endpoint(apartment_id: str) -> Apartment:
    return await get_Apartment_id(apartment_id)


# Actualizar un apartamento 
@router.put("/apartments/{apartment_id}", response_model=Apartment, tags=["🏢 Apartments"])
@validateuser 
async def update_apartment_endpoint(request: Request, apartment_id: str, apartment: Apartment) -> Apartment:
    return await update_Apartment(apartment_id, apartment)


# Desactivar o eliminar un apartamento
@router.delete("/apartments/{apartment_id}", response_model=dict)
async def delete_apartment_endpoint(apartment_id: str):
    return await delete_or_deactivate_apartment(apartment_id)

@router.put("/apartments/{apartment_id}/status", response_model=dict, tags=["🏢 Apartments"])
async def toggle_apartment_status_endpoint(apartment_id: str, status: dict = Body(...)):
    from controllers.Apartment import toggle_apartment_status
    return await toggle_apartment_status(apartment_id, status)