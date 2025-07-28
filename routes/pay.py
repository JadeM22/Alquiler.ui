from fastapi import APIRouter, Request
from utils.security import validateuser, validateadmin
from models.pay import Pay
from controllers.pay import (
    get_Pay,
    get_Pay_by_id_contract,
    create_pay,
    update_Pay
)

router = APIRouter()

@router.get("/contratos/{contract_id}/pagos", response_model=list[Pay])
@validateuser
async def read_pays_by_contract(request: Request, contract_id: str):
    """
    Devuelve todos los pagos asociados a un contrato.
    - Admin puede ver todos.
    - Usuario solo puede ver los de sus contratos.
    """
    return await get_Pay(request, contract_id)


# ✅ GET /contratos/{contract_id}/pagos/{pay_id} → Obtiene un pago específico de un contrato
@router.get("/contratos/{contract_id}/pagos/{pay_id}", response_model=Pay)
@validateuser
async def read_pay_by_contract(request: Request, contract_id: str, pay_id: str):
    """
    Devuelve un pago específico perteneciente a un contrato.
    - Admin puede ver cualquier pago.
    - Usuario solo si es dueño del contrato.
    """
    return await get_Pay_by_id_contract(request, contract_id, pay_id)


# ✅ Crear un pago (SOLO ADMIN)
@router.post("/contratos/{contract_id}/pagos", response_model=Pay)
@validateadmin
async def route_create_pay(request: Request, contract_id: str, pay: Pay):
    return await create_pay(request, contract_id, pay)


# ✅ Actualizar un pago (SOLO ADMIN)
@router.put("/pagos/{pay_id}", response_model=Pay)
@validateuser
async def route_update_pay(request: Request, pay_id: str, pay: Pay):
    return await update_Pay(request, pay_id, pay)
