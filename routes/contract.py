from fastapi import APIRouter, Request
from models.contract import Contract
from utils.security import validateuser
from controllers.contract import (
    get_contracts,
    create_contract,
    get_contract_by_id,
    update_contract,
    delete_or_deactivate_contract  # importamos la nueva función
)

router = APIRouter()

# -----------------------
# Listar todos los contratos
# -----------------------
@router.get("/contracts", response_model=list[Contract])
@validateuser
async def read_contracts(request: Request):
    return await get_contracts(request)


# -----------------------
# Crear un nuevo contrato
# -----------------------
@router.post("/contracts", response_model=Contract)
@validateuser
async def create_contract_endpoint(request: Request, contract: Contract):
    return await create_contract(request, contract)


# -----------------------
# Obtener contrato por ID
# -----------------------
@router.get("/contracts/{contract_id}", response_model=Contract)
@validateuser
async def get_contract_by_id_endpoint(request: Request, contract_id: str) -> Contract:
    return await get_contract_by_id(request, contract_id)


# -----------------------
# Actualizar contrato
# -----------------------
@router.put("/contracts/{contract_id}", response_model=Contract)
@validateuser
async def update_contract_endpoint(request: Request, contract_id: str, contract: Contract):
    return await update_contract(request, contract_id, contract)


# -----------------------
# Eliminar o desactivar contrato
# -----------------------
@router.delete("/contracts/{contract_id}", response_model=dict)
@validateuser
async def delete_contract_endpoint(contract_id: str):
    """
    Desactiva el contrato si tiene apartamentos asignados,
    lo elimina si no tiene apartamentos.
    """
    return await delete_or_deactivate_contract(contract_id)
