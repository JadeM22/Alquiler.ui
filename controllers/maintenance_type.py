from fastapi import HTTPException
from utils.mongodb import get_collection
from models.maintenance_type import Maintenance_Type
from bson import ObjectId

type_coll = get_collection("maintenance_types")

# ✅ Obtener todos los tipos de mantenimiento activos
async def get_all_maintenance_types() -> list[Maintenance_Type]:
    try:
        types = []
        for doc in type_coll.find({"active": True}):
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            types.append(Maintenance_Type(**doc))
        return types
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo tipos de mantenimiento: {str(e)}")

# ✅ Obtener un tipo de mantenimiento por ID
async def get_maintenance_type_by_id(type_id: str) -> Maintenance_Type:
    try:
        doc = type_coll.find_one({"_id": ObjectId(type_id), "active": True})
        if not doc:
            raise HTTPException(status_code=404, detail="Tipo de mantenimiento no encontrado")
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return Maintenance_Type(**doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo tipo de mantenimiento: {str(e)}")

# ✅ Crear un nuevo tipo de mantenimiento
async def create_maintenance_type(m_type: Maintenance_Type) -> Maintenance_Type:
    try:
        m_dict = m_type.model_dump(exclude={"id"})

        # Verificar si ya existe un tipo con la misma descripción
        if type_coll.find_one({"description": {"$regex": f"^{m_dict['description']}$", "$options": "i"}}):
            raise HTTPException(status_code=400, detail="Ya existe un tipo de mantenimiento con esta descripción")

        inserted = type_coll.insert_one(m_dict)
        m_type.id = str(inserted.inserted_id)
        return m_type
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando tipo de mantenimiento: {str(e)}")

# ✅ Actualizar un tipo de mantenimiento
async def update_maintenance_type(type_id: str, m_type: Maintenance_Type) -> Maintenance_Type:
    try:
        m_dict = m_type.model_dump(exclude={"id"})
        result = type_coll.update_one({"_id": ObjectId(type_id)}, {"$set": m_dict})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Tipo de mantenimiento no encontrado")
        return await get_maintenance_type_by_id(type_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando tipo de mantenimiento: {str(e)}")

# ✅ Desactivar un tipo de mantenimiento
async def deactivate_maintenance_type(type_id: str) -> Maintenance_Type:
    try:
        result = type_coll.update_one({"_id": ObjectId(type_id)}, {"$set": {"active": False}})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Tipo de mantenimiento no encontrado")
        return await get_maintenance_type_by_id(type_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error desactivando tipo de mantenimiento: {str(e)}")

