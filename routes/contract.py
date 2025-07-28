from fastapi import APIRouter, Request
from models.contract import Contract
from utils.security import validateuser, validateadmin
from controllers.contract import (
    get_Contracts,
    create_Contract,
    get_Contract_by_id,
    update_Contract
)

router = APIRouter()

@router.get("/contratos", response_model=list[Contract])
@validateadmin
async def read_contracts(request: Request):
    return await get_Contracts(request)

@router.post("/contratos", response_model=Contract)
@validateadmin
async def create_contract_endpoint(request: Request, contract: Contract):
    return await create_Contract(request, contract)

@router.get("/contract/{contract_id}", response_model=Contract)
@validateuser
async def get_contract_by_id_endpoint(request: Request, contract_id: str) -> Contract:
    return await get_Contract_by_id(contract_id)


@router.put("/contratos/{contract_id}", response_model=Contract)
@validateadmin
async def update_contract_endpoint(request: Request, contract_id: str, contract: Contract):
    return await update_Contract(request, contract_id, contract)
