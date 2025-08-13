from bson import ObjectId

def get_apartment_pipeline() -> list:
    return [
        {
            "$addFields": {
                "id": {"$toString": "$_id"}
            }
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
            "$group": {
                "_id": {
                    "id": "$id",
                    "number": "$number",
                    "level": "$level",
                    "status": "$status"
                },
                "contracts": {
                    "$sum": {"$size": "$contracts_list"}
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": "$_id.id",
                "number": "$_id.number",
                "level": "$_id.level",
                "status": "$_id.status",
                "contracts": 1
            }
        }
    ]

def validate_apartment_has_contracts_pipeline(id: str) -> list:
    return [
        {
            "$match": {
                "_id": ObjectId(id)
            }
        },
        {
            "$addFields": {
                "id": {"$toString": "$_id"}
            }
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
            "$group": {
                "_id": {
                    "id": "$id",
                    "number": "$number",
                    "level": "$level",
                    "status": "$status"
                },
                "contracts": {
                    "$sum": {"$size": "$contracts_list"}
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": "$_id.id",
                "number": "$_id.number",
                "level": "$_id.level",
                "status": "$_id.status",
                "contracts": 1
            }
        }
    ]
