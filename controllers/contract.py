from models.contract import Contract
from utils.mongodb import get_collection
from fastapi import HTTPException, Request
from bson import ObjectId
from datetime import datetime

coll = get_collection("contracts")

# ✅ GET /contracts → Admin ve todos, usuario solo los suyos
async def get_contracts(request: Request) -> list[Contract]:
    try:
        user_id = str(request.state.id)
        admin = getattr(request.state, "admin", False)

        query = {} if admin else {"id_User": user_id}
        contracts = []

        for doc in coll.find(query):
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            contracts.append(Contract(**doc))

        return contracts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching contracts: {e}")

# ✅ GET /contracts/{id} → Admin ve cualquiera, usuario solo los suyos
async def get_contract_by_id(request: Request, contract_id: str) -> Contract:
    try:
        doc = coll.find_one({"_id": ObjectId(contract_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Contract not found")

        admin = getattr(request.state, "admin", False)
        user_id = str(request.state.id)
        if not admin and doc.get("id_User") != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this contract")

        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return Contract(**doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching contract: {e}")

# ✅ POST /contracts → Solo admins pueden crear
async def create_contract(request: Request, contract: Contract) -> Contract:
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(status_code=403, detail="Only admins can create contracts")

        contract_dict = contract.model_dump(exclude={"id"})

        # 🔹 Convertir fechas a datetime antes de guardar
        if contract_dict.get("start_date"):
            contract_dict["start_date"] = datetime.combine(contract_dict["start_date"], datetime.min.time())
        if contract_dict.get("end_date"):
            contract_dict["end_date"] = datetime.combine(contract_dict["end_date"], datetime.min.time())

        inserted = coll.insert_one(contract_dict)
        contract.id = str(inserted.inserted_id)
        return contract
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating contract: {e}")

# ✅ PUT /contracts/{id} → Solo admins pueden actualizar
async def update_contract(request: Request, contract_id: str, contract: Contract) -> Contract:
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(status_code=403, detail="Only admins can update contracts")

        contract_dict = contract.model_dump(exclude={"id"})

        # 🔹 Convertir fechas a datetime antes de actualizar
        if contract_dict.get("start_date"):
            contract_dict["start_date"] = datetime.combine(contract_dict["start_date"], datetime.min.time())
        if contract_dict.get("end_date"):
            contract_dict["end_date"] = datetime.combine(contract_dict["end_date"], datetime.min.time())

        result = coll.update_one({"_id": ObjectId(contract_id)}, {"$set": contract_dict})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contract not found")

        return await get_contract_by_id(request, contract_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating contract: {e}")
