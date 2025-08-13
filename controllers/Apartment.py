from models.Apartment import Apartment
from utils.mongodb import get_collection
from fastapi import HTTPException
from bson import ObjectId

from pipelines.apartments_pipelines import (
    get_apartment_pipeline,
    validate_apartment_has_contracts_pipeline
)

coll = get_collection("apartments")

# -----------------------
# Crear apartamento
# -----------------------
async def create_Apartment(apartment: Apartment) -> Apartment:
    try:
        apartment.number = apartment.number.strip().lower()

        existing_apartment = coll.find_one({"number": apartment.number})
        if existing_apartment:
            raise HTTPException(status_code=400, detail="Apartment already exists")

        apartment_dict = apartment.model_dump(exclude={"id"})
        inserted = coll.insert_one(apartment_dict)
        apartment.id = str(inserted.inserted_id)

        return apartment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating apartment: {str(e)}")


# -----------------------
# Obtener todos los apartamentos
# -----------------------
async def get_Apartment() -> list[Apartment]:
    try:
        pipeline = get_apartment_pipeline()
        apartments = list(coll.aggregate(pipeline))
        return [Apartment(**doc) for doc in apartments]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching apartments: {str(e)}")


# -----------------------
# Obtener un apartamento por ID
# -----------------------
async def get_Apartment_id(apartment_id: str) -> Apartment:
    try:
        doc = coll.find_one({"_id": ObjectId(apartment_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Apartment not found")

        doc['id'] = str(doc['_id'])
        del doc['_id']
        return Apartment(**doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching apartment: {str(e)}")


# -----------------------
# Actualizar un apartamento
# -----------------------
async def update_Apartment(apartment_id: str, apartment: Apartment) -> Apartment:
    try:
        apartment.number = apartment.number.strip().lower()

        existing_apartment = coll.find_one({
            "number": apartment.number,
            "_id": {"$ne": ObjectId(apartment_id)}
        })
        if existing_apartment:
            raise HTTPException(status_code=400, detail="Apartment already exists")

        result = coll.update_one(
            {"_id": ObjectId(apartment_id)},
            {"$set": apartment.model_dump(exclude={"id"})}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Apartment not found")

        return await get_Apartment_id(apartment_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating apartment: {str(e)}")


# -----------------------
# Desactivar o eliminar un apartamento
# -----------------------
async def deactivate_Apartment(apartment_id: str) -> dict:
    try:
        pipeline = validate_apartment_has_contracts_pipeline(apartment_id)
        assigned = list(coll.aggregate(pipeline))

        if assigned is None or len(assigned) == 0:
            raise HTTPException(status_code=404, detail="Apartment not found")

        if assigned[0]["number_of_contracts"] > 0:
            coll.update_one(
                {"_id": ObjectId(apartment_id)},
                {"$set": {"status": "inactive"}}
            )
            return {"message": "Apartment has contracts and has been deactivated"}
        else:
            coll.delete_one({"_id": ObjectId(apartment_id)})
            return {"message": "Apartment deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating apartment: {str(e)}")
