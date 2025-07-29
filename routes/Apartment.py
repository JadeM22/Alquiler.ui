from fastapi import APIRouter, HTTPException, Request, Query
from models.Apartment import Apartment
from controllers.Apartment import (
    create_Apartment,
    get_Apartment,
    get_Apartment_id,
    update_Apartment,
    deactivate_Apartment
)
from utils.security import validateadmin
from pipelines.check_maintenance import check_maintenance_pipeline
from pipelines.public import get_apartments_public

router = APIRouter()

# Crear un nuevo apartamento (solo administradores)
@router.post("/apartments", response_model=Apartment, tags=["🏢 Apartments"])
@validateadmin   
async def create_apartment_endpoint(request: Request, apartment: Apartment) -> Apartment:
    return await create_Apartment(apartment)


# Obtener todos los apartamentos (público)
@router.get("/apartments", response_model=list[Apartment], tags=["🏢 Apartments"])
async def get_apartments_endpoint() -> list[Apartment]:
    return await get_Apartment()


# Obtener un apartamento por ID (público)
@router.get("/apartments/{apartment_id}", response_model=Apartment, tags=["🏢 Apartments"])
async def get_apartment_by_id_endpoint(apartment_id: str) -> Apartment:
    return await get_Apartment_id(apartment_id)


# Actualizar un apartamento (solo administradores)
@router.put("/apartments/{apartment_id}", response_model=Apartment, tags=["🏢 Apartments"])
@validateadmin   
async def update_apartment_endpoint(request: Request, apartment_id: str, apartment: Apartment) -> Apartment:
    return await update_Apartment(apartment_id, apartment)


# Desactivar un apartamento (solo administradores)
@router.delete("/apartments/{apartment_id}", response_model=Apartment, tags=["🏢 Apartments"])
@validateadmin   
async def deactivate_apartment_endpoint(request: Request, apartment_id: str) -> Apartment:
    return await deactivate_Apartment(apartment_id)


@router.get("/apartments/{apartment_id}/check_maintenance",tags=["🏢 Apartments"])
async def check_maintenance(apartment_id: str):
    return await check_maintenance_pipeline(apartment_id)

@router.get("/apartamentos", tags=[ "🌐 Public"])
async def get_apartments_public_endpoint(
    active: str | None = Query(None, description="Filtrar por estado del apartamento (true/false)"),
    limit: int = Query(10, ge=1, le=100, description="Límite de resultados"),
    skip: int = Query(0, ge=0, description="Resultados a omitir")
):
    """Lista pública de apartamentos con filtros y paginación (sin token)."""
    return await get_apartments_public(active=active, limit=limit, skip=skip)