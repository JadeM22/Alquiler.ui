from models.contract import Contract
from utils.mongodb import get_collection
from fastapi import HTTPException, Request
from bson import ObjectId
from datetime import datetime
from pymongo.collection import Collection
from pipelines.contract_pipelines import validate_contract_has_apartments_pipeline  

coll: Collection = get_collection("contracts")

# Lista todos los contratos
async def get_contracts(request: Request) -> list[Contract]:
    """Obtiene todos los contratos (público, sin validaciones de usuario)."""
    try:
        contracts = []

        for doc in coll.find({}): 
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)

            try:
                contracts.append(Contract(**doc))  
            except Exception as e:
                print(f"Contrato con datos incompletos: {doc} - Error: {e}")

        return contracts

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los contratos: {e}")

# Lista un contrato en específico
async def get_contract_by_id(request: Request, contract_id: str) -> Contract:
    """Obtiene un contrato específico (admin ve todos, usuario solo los suyos)."""
    try:
        doc = coll.find_one({"_id": ObjectId(contract_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")

        admin = getattr(request.state, "admin", False)
        user_id = str(request.state.id)
        if not admin and doc.get("id_user") != user_id:
            raise HTTPException(status_code=403, detail="No autorizado a ver este contrato")

        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return Contract(**doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el contrato: {e}")

# Crea un nuevo contrato 
async def create_contract(contract: Contract) -> Contract:
    try:
        contract_dict = contract.model_dump(exclude={"id"})

        if contract_dict.get("start_date"):
            contract_dict["start_date"] = datetime.combine(contract_dict["start_date"], datetime.min.time())
        if contract_dict.get("end_date"):
            contract_dict["end_date"] = datetime.combine(contract_dict["end_date"], datetime.min.time())

        inserted = coll.insert_one(contract_dict)
        contract.id = str(inserted.inserted_id)
        return contract

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el contrato: {e}")

# Actualiza un contrato
async def update_contract(contract_id: str, contract: Contract) -> Contract:
    try:
        contract_dict = contract.model_dump(exclude={"id"})

        if contract_dict.get("start_date"):
            contract_dict["start_date"] = datetime.combine(contract_dict["start_date"], datetime.min.time())
        if contract_dict.get("end_date"):
            contract_dict["end_date"] = datetime.combine(contract_dict["end_date"], datetime.min.time())

        result = coll.update_one({"_id": ObjectId(contract_id)}, {"$set": contract_dict})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")

        updated_doc = coll.find_one({"_id": ObjectId(contract_id)})
        updated_doc["id"] = str(updated_doc["_id"])
        updated_doc.pop("_id", None)

        return Contract(**updated_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar contrato: {e}")


# Desactiva o elimina un contrato según tenga apartamentos
async def delete_or_deactivate_contract(contract_id: str) -> dict:
    """Elimina cualquier contrato sin validaciones."""
    try:
        contract = coll.find_one({"_id": ObjectId(contract_id)})
        if not contract:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")

        # Revisar si tiene apartamentos asignados
        pipeline = validate_contract_has_apartments_pipeline(contract_id)
        assigned = list(coll.aggregate(pipeline))
        num_apts = assigned[0]["number_of_apartments"] if assigned else 0

        if num_apts > 0:
            coll.update_one(
                {"_id": ObjectId(contract_id)},
                {"$set": {"status": "inactive"}}
            )
            return {"message": "Contrato tiene apartamentos y ha sido desactivado"}
        else:
            coll.delete_one({"_id": ObjectId(contract_id)})
            return {"message": "Contrato eliminado exitosamente"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar el contrato: {e}"
        )

