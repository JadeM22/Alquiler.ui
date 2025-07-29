from utils.mongodb import get_collection
from bson import ObjectId
from fastapi import HTTPException

apartments_coll = get_collection("apartments")

async def check_maintenance_pipeline(apartment_id: str):
    try:
        try:
            oid_apartment = ObjectId(apartment_id)
        except:
            raise HTTPException(status_code=400, detail="ID de apartamento inválido")

        pipeline = [
            {"$match": {"_id": oid_apartment}},
            {"$lookup": {
                    "from": "maintenance",
                    "localField": "_id",
                    "foreignField": "apartment_id",
                    "as": "maintenances"
                }
            },
            {"$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                    "pending_count": {"$size": {"$filter": {
                                "input": "$maintenances",
                                "cond": {"$eq": ["$$this.status", "pending"]}
                            }
                        }
                    }
                }
            },
            {"$match": {"pending_count": {"$gt": 2}}}
        ]

        result = list(apartments_coll.aggregate(pipeline))
        if not result:
            return {"message": "El apartamento tiene 2 o menos mantenimientos pendientes."}
        else:
            return {
                "message": "El apartamento tiene más de 2 mantenimientos pendientes. Requiere atención.",
                "data": result[0]
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validando mantenimiento: {str(e)}")

