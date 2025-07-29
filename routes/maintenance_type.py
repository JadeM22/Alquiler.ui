from fastapi import APIRouter, Request
from utils.security import validateuser, validateadmin
from models.maintenance_type import Maintenance_Type
from controllers.maintenance_type import (
    get_all_maintenance_types,
    get_maintenance_type_by_id,
    create_maintenance_type,
    update_maintenance_type,
    deactivate_maintenance_type,
   
)

router = APIRouter()

@router.get("/maintenance_types", response_model=list[Maintenance_Type])
@validateuser
async def list_maintenance_types(request: Request):
    return await get_all_maintenance_types()

@router.get("/maintenance_types/{type_id}", response_model=Maintenance_Type)
@validateuser
async def get_maintenance_type(type_id: str, request: Request):
    return await get_maintenance_type_by_id(type_id)

@router.post("/maintenance_types", response_model=Maintenance_Type)
@validateadmin
async def create_maintenance_type_endpoint(request: Request, mt: Maintenance_Type):
    return await create_maintenance_type(mt)

@router.put("/maintenance_types/{type_id}", response_model=Maintenance_Type)
@validateadmin
async def update_maintenance_type_endpoint(request: Request, type_id: str, mt: Maintenance_Type):
    return await update_maintenance_type(request, type_id, mt)

@router.delete("/maintenance_types/{type_id}", response_model=Maintenance_Type)
@validateadmin
async def deactivate_maintenance_type_endpoint(request: Request, type_id: str):
    return await deactivate_maintenance_type(request, type_id)
