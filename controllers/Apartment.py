from models.Apartment import Apartment
from utils.mongodb import get_collection
from fastapi import HTTPException
from bson import ObjectId

coll = get_collection("apartments")

# Crea un nuevo apartamento
async def create_Apartment(apartment: Apartment) -> Apartment:
    """Crea un nuevo apartamento (solo administradores)."""
    try:
        # Normalizar número de apartamento
        apartment.number = apartment.number.strip().lower()

        # Verificar si ya existe
        existing_apartment = coll.find_one({"number": apartment.number})
        if existing_apartment:
            raise HTTPException(status_code=400, detail="El apartamento ya existe")

        # Convertir a diccionario y asegurar que photo_url sea string
        apartment_dict = apartment.model_dump(exclude={"id"})
        if "photo_url" in apartment_dict and apartment_dict["photo_url"] is not None:
            apartment_dict["photo_url"] = str(apartment_dict["photo_url"])

        # Insertar en MongoDB
        inserted = coll.insert_one(apartment_dict)
        apartment.id = str(inserted.inserted_id)

        return apartment

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando apartamento: {str(e)}")


# Desactiva un apartamento 
async def deactivate_Apartment(apartment_id: str) -> Apartment:
    """Desactiva un apartamento (solo administradores)."""
    try:
        # Intentamos actualizar el campo enabled a False
        result = coll.update_one(
            {"_id": ObjectId(apartment_id)},
            {"$set": {"enabled": False}}
        )

        # Si no encontró el documento, lanzamos error
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Apartamento no encontrado")

        # Retornamos el apartamento actualizado
        return await get_Apartment_id(apartment_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error desactivando apartamento: {str(e)}")


#Lista los apartamentos 
async def get_Apartment() -> list[Apartment]:
    """Obtiene todos los apartamentos (publico)."""
    try:
        apartments = []
        for doc in coll.find():
            doc["id"] = str(doc["_id"])
            del doc["_id"]

            # Convertimos photo_url a string si existe
            if "photo_url" in doc and doc["photo_url"] is not None:
                doc["photo_url"] = str(doc["photo_url"])

            apartments.append(Apartment(**doc))
        return apartments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo apartamentos: {str(e)}")


#lista un apartamento en especifico
async def get_Apartment_id(apartment_id: str) -> Apartment:
    """Obtiene un apartamento en especifico (admin ve todos, usuario solo los suyos)."""
    try:
        doc = coll.find_one({"_id": ObjectId(apartment_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Apartamento no encontrado")

        doc["id"] = str(doc["_id"])
        del doc["_id"]

        # Convertimos photo_url a string si existe
        if "photo_url" in doc and doc["photo_url"] is not None:
            doc["photo_url"] = str(doc["photo_url"])

        return Apartment(**doc)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo apartamento: {str(e)}")


# Actualiza un apartamento en especifico
async def update_Apartment(apartment_id: str, apartment: Apartment) -> Apartment:
    """Actualiza los datos de un apartamento (Solo administradores)."""
    try:
        # Normalizamos el número a minúsculas
        apartment.number = apartment.number.strip().lower()

        # Verificar que no exista otro apartamento con el mismo número
        existing = coll.find_one({
            "number": apartment.number,
            "_id": {"$ne": ObjectId(apartment_id)}
        })
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe un apartamento con este número")

        # Convertimos HttpUrl a str antes de guardar
        apartment_dict = apartment.model_dump(exclude={"id"})
        if apartment_dict.get("photo_url") is not None:
            apartment_dict["photo_url"] = str(apartment_dict["photo_url"])

        # Ejecutar actualización
        result = coll.update_one({"_id": ObjectId(apartment_id)}, {"$set": apartment_dict})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Apartamento no encontrado")

        # Retornar el apartamento actualizado
        return await get_Apartment_id(apartment_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando apartamento: {str(e)}")


