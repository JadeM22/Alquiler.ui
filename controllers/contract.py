from models.contract import Contract
from utils.mongodb import get_collection
from fastapi import HTTPException, Request
from bson import ObjectId
from datetime import datetime
from bson.errors import InvalidId

coll = get_collection("contracts")

# ✅ GET /contratos → Admin ve todos, usuario solo los suyos
async def get_Contracts(request: Request) -> list[Contract]:
    try:
        user_id = request.state.id
        admin = getattr(request.state, "admin", False)

        query = {} if admin else {"id_User": user_id}  # 🔹 CAMBIO AQUÍ
        contracts = []

        for doc in coll.find(query):
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            contracts.append(Contract(**doc))

        return contracts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo contratos: {str(e)}")


# ✅ GET /contratos/{id} → Admin ve cualquier contrato, usuario solo los suyos
async def get_Contract_by_id(contract_id: str) -> Contract:
    try:
        doc = coll.find_one({"_id": ObjectId(contract_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Catalog type not found")

        # Mapear _id a id para el modelo Pydantic
        doc['id'] = str(doc['_id'])
        del doc['_id']
        return Contract(**doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching contract: {str(e)}")



# ✅ POST /contratos → Solo administradores pueden crear contratos
async def create_Contract(request: Request, contract: Contract) -> Contract:
    try:
        admin = getattr(request.state, "admin", False)
        if not admin:
            raise HTTPException(status_code=403, detail="Solo administradores pueden crear contratos")

        contract_dict = contract.model_dump(exclude={"id"})

        # 🔹 Convertir fechas a datetime
        if "start_date" in contract_dict and contract_dict["start_date"]:
            contract_dict["start_date"] = datetime.combine(contract_dict["start_date"], datetime.min.time())
        if "end_date" in contract_dict and contract_dict["end_date"]:
            contract_dict["end_date"] = datetime.combine(contract_dict["end_date"], datetime.min.time())

        inserted = coll.insert_one(contract_dict)
        contract.id = str(inserted.inserted_id)
        return contract
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando contrato: {str(e)}")


# ✅ PUT /contratos/{id} → Solo administradores
async def update_Contract(request: Request, contract_id: str, contract: Contract) -> Contract:
    try:
        admin = getattr(request.state, "admin", False)
        if not admin:
            raise HTTPException(status_code=403, detail="Solo administradores pueden actualizar contratos")

        contract_dict = contract.model_dump(exclude={"id"})

        # 🔹 Convertir fechas a datetime antes de actualizar
        if "start_date" in contract_dict and contract_dict["start_date"]:
            contract_dict["start_date"] = datetime.combine(contract_dict["start_date"], datetime.min.time())
        if "end_date" in contract_dict and contract_dict["end_date"]:
            contract_dict["end_date"] = datetime.combine(contract_dict["end_date"], datetime.min.time())

        result = coll.update_one({"_id": ObjectId(contract_id)}, {"$set": contract_dict})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")

        return await get_Contract_by_id(request, contract_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando contrato: {str(e)}")

