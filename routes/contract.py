from fastapi import APIRouter, Request
from models.contract import Contract
from controllers.contract import (
    get_contracts,
    create_contract,
    get_contract_by_id,
    update_contract,
    delete_or_deactivate_contract
)

router = APIRouter()


# Listar todos los contratos
@router.get("/contracts", response_model=list[Contract])
async def read_contracts(request: Request):
    return await get_contracts(request)

# Crear un nuevo contrato 
@router.post("/contracts", response_model=Contract)
async def create_contract_endpoint(contract: Contract):
    return await create_contract(contract)


# Obtener contrato por ID 
@router.get("/contracts/{contract_id}", response_model=Contract)
async def get_contract_by_id_endpoint(request: Request, contract_id: str) -> Contract:
    return await get_contract_by_id(request, contract_id)

# Actualizar contrato
@router.put("/contracts/{contract_id}", response_model=Contract)
async def update_contract_endpoint(contract_id: str, contract: Contract):
    return await update_contract(contract_id, contract)


# Eliminar o desactivar contrato 
@router.delete("/contracts/{contract_id}", response_model=dict)
async def delete_contract_endpoint(contract_id: str):
    return await delete_or_deactivate_contract(contract_id)
