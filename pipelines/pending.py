from utils.mongodb import get_collection

coll = get_collection("pays")

async def get_pays_pending_validation(request):
    """Devuelve pagos pendientes o contratos inactivos."""
    pipeline = [
        {
            "$lookup": {
                "from": "contracts",
                "let": {"cid": "$id_Contract"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", {"$toObjectId": "$$cid"}]}}}
                ],
                "as": "contract_info"
            }
        },
        {"$unwind": "$contract_info"},
        {"$match": {"$or": [{"is_paid": False}, {"contract_info.active": False}]}},
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "cost": 1,
                "is_paid": 1,
                "contract_active": "$contract_info.active",
                "contract_id": {"$toString": "$contract_info._id"}
            }
        }
    ]
    return list(coll.aggregate(pipeline))
