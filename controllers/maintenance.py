from fastapi import HTTPException, Request
from bson import ObjectId
from utils.mongodb import get_collection
from models.maintenance import Maintenance

maintenance_coll = get_collection("maintenance")
type_coll = get_collection("maintenance_types")
contracts_coll = get_collection("contracts")  


# Función auxiliar para verificar si el mantenimiento pertenece al usuario
def maintenance_belongs_to_user(maintenance_doc, user_id: str) -> bool:
    contract_id = maintenance_doc.get("id_Contract")
    if not contract_id:
        return False
    contract = contracts_coll.find_one({"_id": ObjectId(contract_id)})
    return contract and str(contract.get("id_User")) == str(user_id)


# Lista todos los mantenimientos
async def get_all_maintenances(request: Request) -> list[Maintenance]:
    """Obtiene todos los mantenimientos (admin ve todos, usuario solo los suyos)."""
    try:
        user_id = request.state.id
        admin = getattr(request.state, "admin", False)
        maintenances = []

        print("DEBUG → user_id:", user_id, "| admin:", admin)

        if admin:
            cursor = maintenance_coll.find({})
        else:
            # Buscar contratos donde el usuario sea propietario (acepta str y ObjectId)
            user_contracts = contracts_coll.find({
                "$or": [
                    {"id_User": ObjectId(user_id)},
                    {"id_User": user_id}
                ]
            })

            contract_ids = [str(c["_id"]) for c in user_contracts]

            print("DEBUG → contratos encontrados:", contract_ids)

            if not contract_ids:
                return []

            # Buscar mantenimientos relacionados con esos contratos
            cursor = maintenance_coll.find({
                "$or": [
                    {"id_Contract": {"$in": contract_ids}},
                    {"id_Contract": {"$in": [ObjectId(cid) for cid in contract_ids]}}
                ]
            })

        for doc in cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            maintenances.append(Maintenance(**doc))

        print(f"DEBUG → encontrados {len(maintenances)} mantenimientos")
        return maintenances

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo mantenimientos: {str(e)}")



# Lista un mantenimiento en especifico
async def get_maintenance_by_id(request: Request, maintenance_id: str) -> Maintenance:
    """Obtiene un mantenimiento en especifico (admin ve todos, usuario solo los suyos)."""
    try:
        user_id = request.state.id
        admin = getattr(request.state, "admin", False)

        doc = maintenance_coll.find_one({"_id": ObjectId(maintenance_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

        if not admin and not maintenance_belongs_to_user(doc, user_id):
            raise HTTPException(status_code=403, detail="No autorizado para ver este mantenimiento")

        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return Maintenance(**doc)

    except HTTPException:
        # Propaga las excepciones HTTP tal cual
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo mantenimiento: {str(e)}")
    

# Crea un nuevo mantenimiento
async def create_maintenance(request: Request, m: Maintenance) -> Maintenance:
    """Crea un nuevo mantenimiento (solo administradores)."""
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(status_code=403, detail="Solo administradores pueden crear mantenimientos")

        # Validar tipo de mantenimiento
        maintenance_type_doc = type_coll.find_one({"_id": ObjectId(m.id_Maintenance_type), "active": True})
        if not maintenance_type_doc:
            raise HTTPException(status_code=400, detail="Tipo de mantenimiento inválido o inactivo")

        # Validar contrato
        contract_doc = contracts_coll.find_one({"_id": ObjectId(m.id_Contract)})
        if not contract_doc:
            raise HTTPException(status_code=400, detail="Contrato no existe")

        m_dict = m.model_dump(exclude={"id"})
        inserted = maintenance_coll.insert_one(m_dict)
        m.id = str(inserted.inserted_id)
        return m
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando mantenimiento: {str(e)}")



#  actualizar mantenimiento 
async def update_maintenance(request: Request, maintenance_id: str, m: Maintenance) -> Maintenance:
    """Actualiza un mantenimiento (solo administradores)."""
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(status_code=403, detail="Solo administradores pueden actualizar mantenimientos")

        # Validar tipo de mantenimiento
        maintenance_type_doc = type_coll.find_one({"_id": ObjectId(m.id_Maintenance_type), "active": True})
        if not maintenance_type_doc:
            raise HTTPException(status_code=400, detail="Tipo de mantenimiento inválido o inactivo")

        result = maintenance_coll.update_one(
            {"_id": ObjectId(maintenance_id)},
            {"$set": m.model_dump(exclude={"id"})}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

        return await get_maintenance_by_id(request, maintenance_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando mantenimiento: {str(e)}")


# desactivar mantenimiento
async def deactivate_maintenance(request: Request, maintenance_id: str) -> Maintenance:
    """Desactiva un mantenimiento (solo administradores)."""
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(status_code=403, detail="Solo administradores pueden desactivar mantenimientos")

        result = maintenance_coll.update_one(
            {"_id": ObjectId(maintenance_id)},
            {"$set": {"active": False}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

        return await get_maintenance_by_id(request, maintenance_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error desactivando mantenimiento: {str(e)}")
