from fastapi import Request, HTTPException
from bson import ObjectId
from utils.mongodb import get_collection

coll = get_collection("pays")
contracts_coll = get_collection("contracts")

async def get_pays_with_contract_details(request: Request, contract_id: str):
    """Obtiene pagos de un contrato con detalles de contrato usando $lookup."""
    user_id = str(request.state.id)
    admin = getattr(request.state, "admin", False)

    try:
        oid_contract = ObjectId(contract_id)
    except:
        oid_contract = None

    contract = contracts_coll.find_one({"_id": oid_contract})
    if not contract:
        raise HTTPException(404, "Contrato no encontrado")
    if not admin and str(contract.get("id_User")) != user_id:
        raise HTTPException(403, "No autorizado")

    pipeline = [
        {"$match": {"$or": [{"id_Contract": contract_id}, {"contract_id": contract_id}]}},
        {
            "$lookup": {
                "from": "contracts",
                "let": {"cid1": "$id_Contract", "cid2": "$contract_id"},
                "pipeline": [
                    {"$match": {
                        "$expr": {"$or": [
                            {"$eq": ["$_id", {"$toObjectId": "$$cid1"}]},
                            {"$eq": ["$_id", {"$toObjectId": "$$cid2"}]}
                        ]}
                    }}
                ],
                "as": "contract_info"
            }
        },
        {"$unwind": "$contract_info"},
        {
            "$project": {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "cost": 1,
                "is_paid": 1,
                "date": 1,
                "id_Contract": {
                    "$cond": {
                        "if": {"$eq": [{"$type": "$id_Contract"}, "objectId"]},
                        "then": {"$toString": "$id_Contract"},
                        "else": "$id_Contract"
                    }
                },
                "contract": {
                    "id": {"$toString": "$contract_info._id"},
                    "start_date": "$contract_info.start_date",
                    "active": "$contract_info.active"
                }
            }
        }
    ]

    return list(coll.aggregate(pipeline))
