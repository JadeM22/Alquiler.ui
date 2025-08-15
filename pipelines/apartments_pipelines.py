from bson import ObjectId

def get_apartments_pipeline() -> list:
    """Pipeline para obtener apartamentos con la cantidad de contratos"""
    return [
        {
            "$addFields": {"id": {"$toString": "$_id"}}
        },
        {
            "$lookup": {
                "from": "contracts",
                "localField": "id",
                "foreignField": "id_apartment",
                "as": "contracts_list"
            }
        },
        {
            "$addFields": {
                "number_of_contracts": {"$size": "$contracts_list"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "number": 1,
                "level": 1,
                "status": 1,
                "number_of_contracts": 1
            }
        }
    ]

def validate_apartment_has_contracts_pipeline(apartment_id: str) -> list:
    """Pipeline para validar si un apartamento tiene contratos"""
    return [
        {"$match": {"_id": ObjectId(apartment_id)}},
        {"$addFields": {"id": {"$toString": "$_id"}}},
        {
            "$lookup": {
                "from": "contracts",
                "localField": "id",
                "foreignField": "id_apartment",
                "as": "contracts_list"
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "number": 1,
                "level": 1,
                "status": 1,
                "number_of_contracts": {"$size": "$contracts_list"}
            }
        }
    ]
