from models.contract import Contract
from utils.mongodb import get_collection
from fastapi import HTTPException, Request
from bson import ObjectId
from datetime import datetime
from pipelines.contract_pipelines import validate_contract_has_apartments_pipeline  # tu pipeline
from pymongo.collection import Collection

coll: Collection = get_collection("contracts")

# -----------------------
# Lista todos los contratos
# -----------------------
async def get_contracts(request: Request) -> list[Contract]:
    """Obtiene todos los contratos (admin ve todos, usuario solo los suyos)."""
    try:
        user_id = str(request.state.id)
        admin = getattr(request.state, "admin", False)

        query = {} if admin else {"id_user": user_id}
        contracts = []

        for doc in coll.find(query):
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            contracts.append(Contract(**doc))

        return contracts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los contratos: {e}")


# -----------------------
# Lista un contrato en específico
# -----------------------
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


# -----------------------
# Crea un nuevo contrato
# -----------------------
async def create_contract(request: Request, contract: Contract) -> Contract:
    """Crea un nuevo contrato (solo administradores)."""
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(status_code=403, detail="Solo administradores pueden crear contratos")

        contract_dict = contract.model_dump(exclude={"id"})

        # Convertir fechas a datetime antes de guardar
        if contract_dict.get("start_date"):
            contract_dict["start_date"] = datetime.combine(contract_dict["start_date"], datetime.min.time())
        if contract_dict.get("end_date"):
            contract_dict["end_date"] = datetime.combine(contract_dict["end_date"], datetime.min.time())

        inserted = coll.insert_one(contract_dict)
        contract.id = str(inserted.inserted_id)
        return contract
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el contrato: {e}")


# -----------------------
# Actualiza un contrato
# -----------------------
async def update_contract(request: Request, contract_id: str, contract: Contract) -> Contract:
    """Actualiza un contrato (solo administradores)."""
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(status_code=403, detail="Sólo los administradores pueden actualizar los contratos")

        contract_dict = contract.model_dump(exclude={"id"})

        # Convertir fechas a datetime antes de actualizar
        if contract_dict.get("start_date"):
            contract_dict["start_date"] = datetime.combine(contract_dict["start_date"], datetime.min.time())
        if contract_dict.get("end_date"):
            contract_dict["end_date"] = datetime.combine(contract_dict["end_date"], datetime.min.time())

        result = coll.update_one({"_id": ObjectId(contract_id)}, {"$set": contract_dict})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")

        return await get_contract_by_id(request, contract_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating contract: {e}")


# -----------------------
# Desactiva o elimina un contrato según tenga apartamentos
# -----------------------
async def delete_or_deactivate_contract(contract_id: str) -> dict:
    """Desactiva si el contrato tiene apartamentos asignados, elimina si no."""
    try:
        # Usar pipeline para validar si tiene apartamentos asignados
        pipeline = validate_contract_has_apartments_pipeline(contract_id)
        assigned = list(coll.aggregate(pipeline))

        if not assigned or len(assigned) == 0:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")

        if assigned[0]["number_of_apartments"] > 0:
            coll.update_one(
                {"_id": ObjectId(contract_id)},
                {"$set": {"status": "inactive"}}
            )
            return {"message": "Contrato tiene apartamentos asignados y ha sido desactivado"}
        else:
            coll.delete_one({"_id": ObjectId(contract_id)})
            return {"message": "Contrato eliminado exitosamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el contrato: {str(e)}")
