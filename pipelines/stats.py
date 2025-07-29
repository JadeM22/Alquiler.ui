from fastapi import Request
from bson import ObjectId
from utils.mongodb import get_collection

coll = get_collection("pays")

async def get_pay_stats_by_contract(request: Request, contract_id: str):
    """Usa $group para sumar y promediar pagos de un contrato."""
    try:
        oid_contract = ObjectId(contract_id)
    except:
        oid_contract = None

    pipeline = [
        {"$match": {"$or": [{"id_Contract": contract_id}, {"id_Contract": oid_contract}]}},
        {"$group": {
            "_id": "$id_Contract",
            "total_pagos": {"$sum": 1},
            "suma": {"$sum": "$cost"},
            "promedio": {"$avg": "$cost"}
        }},
        {"$project": {
            "_id": 0,
            "contract_id": "$_id",
            "total_pagos": 1,
            "suma": 1,
            "promedio": 1
        }}
    ]
    return list(coll.aggregate(pipeline))
