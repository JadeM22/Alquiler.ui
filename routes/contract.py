from fastapi import APIRouter, Request
from models.contract import Contract
from utils.security import validateuser, validateadmin
from controllers.contract import (
    get_contracts,
    create_contract,
    get_contract_by_id,
    update_contract
)

router = APIRouter()

@router.get("/contracts", response_model=list[Contract])
@validateadmin
async def read_contracts(request: Request):
    return await get_contracts(request)

@router.post("/contracts", response_model=Contract)
@validateadmin
async def create_contract_endpoint(request: Request, contract: Contract):
    return await create_contract(request, contract)

@router.get("/contracts/{contract_id}", response_model=Contract)
@validateuser
async def get_contract_by_id_endpoint(request: Request, contract_id: str) -> Contract:
    return await get_contract_by_id(request, contract_id)

@router.put("/contracts/{contract_id}", response_model=Contract)
@validateadmin
async def update_contract_endpoint(request: Request, contract_id: str, contract: Contract):
    return await update_contract(request, contract_id, contract)
