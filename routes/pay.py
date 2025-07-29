from fastapi import APIRouter, Request
from utils.security import validateuser, validateadmin
from models.pay import Pay
from controllers.pay import (
    get_Pay, get_Pay_by_id_contract, create_pay, update_Pay,
)

from pipelines.contract_details import get_pays_with_contract_details
from pipelines.stats import get_pay_stats_by_contract
from pipelines.pending import get_pays_pending_validation
from pipelines.payments_stats import get_payments_stats_pipeline


router = APIRouter()

# CRUD - Pagos
@router.get("/contratos/{contract_id}/pagos", response_model=list[Pay], tags=["💰 Payments"])
@validateuser
async def read_pays_by_contract(request: Request, contract_id: str):
    """Obtiene todos los pagos de un contrato"""
    return await get_Pay(request, contract_id)

@router.get("/contratos/{contract_id}/pagos/{pay_id}", response_model=Pay, tags=["💰 Payments"])
@validateuser
async def read_pay_by_contract(request: Request, contract_id: str, pay_id: str):
    """Obtiene un pago específico asociado a un contrato"""
    return await get_Pay_by_id_contract(request, contract_id, pay_id)

@router.post("/contratos/{contract_id}/pagos", response_model=Pay, tags=["💰 Payments"])
@validateadmin
async def route_create_pay(request: Request, contract_id: str, pay: Pay):
    """Crea un pago asociado a un contrato"""
    return await create_pay(request, contract_id, pay)

@router.put("/pagos/{pay_id}", response_model=Pay, tags=["💰 Payments"])
@validateadmin
async def route_update_pay(request: Request, pay_id: str, pay: Pay):
    """Actualiza un pago existente"""
    return await update_Pay(request, pay_id, pay)

# PIPELINES - Operaciones avanzadas
@router.get("/contratos/{contract_id}/pagos-detalles", tags=["📊 Pipeline: Contract Details"])
@validateadmin
async def get_pays_with_contract_info(request: Request, contract_id: str):
    """Devuelve pagos de un contrato con detalles del contrato (lookup)"""
    return await get_pays_with_contract_details(request, contract_id)

@router.get("/contratos/{contract_id}/pagos-estadisticas", tags=["📊 Pipeline: Stats"])
@validateuser
async def get_pay_statistics(request: Request, contract_id: str):
    """Devuelve estadísticas de pagos de un contrato (group)"""
    return await get_pay_stats_by_contract(request, contract_id)

@router.get("/pagos/pendientes-validacion", tags=["📊 Pipeline: Pending Validation"])
@validateadmin
async def get_pays_pending_validation_route(request: Request):
    """Devuelve pagos pendientes de validación o contratos inactivos"""
    return await get_pays_pending_validation(request)

@router.get("/payments/stats", tags=["📊 Pipeline: Stats"])
async def get_payments_stats():
    """Devuelve estadísticas generales de pagos"""
    return await get_payments_stats_pipeline()