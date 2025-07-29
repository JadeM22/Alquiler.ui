from fastapi import APIRouter, Request, Query
from utils.security import validateuser, validateadmin
from models.pay import Pay
from controllers.pay import (
    get_Pay, get_Pay_by_id_contract, create_pay, update_Pay,
    get_pays_with_contract_details, get_pays_public,
    get_pay_stats_by_contract, get_pays_pending_validation
)

router = APIRouter()

# ------- CRUD -------
@router.get("/contratos/{contract_id}/pagos", response_model=list[Pay])
@validateuser
async def read_pays_by_contract(request: Request, contract_id: str):
    """Obtiene todos los pagos de un contrato"""
    print("Admin flag:", getattr(request.state, "admin", False))
    print("User ID:", getattr(request.state, "id", None))
    return await get_Pay(request, contract_id)

@router.get("/contratos/{contract_id}/pagos/{pay_id}", response_model=Pay)
@validateuser
async def read_pay_by_contract(request: Request, contract_id: str, pay_id: str):
    """Obtiene un pago específico asociado a un contrato"""
    return await get_Pay_by_id_contract(request, contract_id, pay_id)

@router.post("/contratos/{contract_id}/pagos", response_model=Pay)
@validateadmin
async def route_create_pay(request: Request, contract_id: str, pay: Pay):
    """Crea un pago asociado a un contrato"""
    return await create_pay(request, contract_id, pay)

@router.put("/pagos/{pay_id}", response_model=Pay)
@validateadmin
async def route_update_pay(request: Request, pay_id: str, pay: Pay):
    """Actualiza un pago existente"""
    return await update_Pay(request, pay_id, pay)

# ------- PIPELINES -------
@router.get("/contratos/{contract_id}/pagos-detalles")
@validateadmin
async def get_pays_with_contract_info(request: Request, contract_id: str):
    """Devuelve pagos de un contrato con detalles del contrato (lookup)"""
    return await get_pays_with_contract_details(request, contract_id)

@router.get("/contratos/{contract_id}/pagos-estadisticas")
@validateuser
async def get_pay_statistics(request: Request, contract_id: str):
    """Devuelve estadísticas de pagos de un contrato (group)"""
    return await get_pay_stats_by_contract(request, contract_id)

@router.get("/pagos/pendientes-validacion")
@validateadmin
async def get_pays_pending_validation_route(request: Request):
    """Devuelve pagos pendientes de validación o contratos inactivos"""
    return await get_pays_pending_validation(request)

# ------- Público con QueryString -------
@router.get("/pagos")
async def get_pagos_public_endpoint(
    status: str | None = Query(None, description="Filtrar por estado del pago (true/false)"),
    limit: int | None = Query(10, ge=1, le=100, description="Límite de resultados"),
    skip: int | None = Query(0, ge=0, description="Resultados a omitir")
):
    """Lista pública de pagos con filtros y paginación"""
    return await get_pays_public(status=status, limit=limit, skip=skip)
