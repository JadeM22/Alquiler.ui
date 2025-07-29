from fastapi import APIRouter, Request, HTTPException
from bson import ObjectId
from utils.mongodb import get_collection
from models.pay import Pay
from typing import List

router = APIRouter()

contracts_coll = get_collection("contracts")
payments_coll = get_collection("pays")  # 🔹 Unificado

@router.get("/contracts/{contract_id}/payments_enriched")
async def get_payments_enriched(contract_id: str, request: Request):
    try:
        # ✅ Validación del ID
        try:
            oid_contract = ObjectId(contract_id)
        except:
            raise HTTPException(status_code=400, detail="ID de contrato inválido")

        # ✅ Pipeline que busca pagos usando id_Contract como string
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"contract_id": contract_id},     # por si algún pago usa este nombre
                        {"id_Contract": contract_id}      # tu campo real
                    ]
                }
            },
            {
                "$lookup": {
                    "from": "contracts",
                    "let": {"cid": "$id_Contract"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$eq": ["$_id", ObjectId(contract_id)]
                                }
                            }
                        }
                    ],
                    "as": "contract_info"
                }
            },
            {"$unwind": "$contract_info"},
            {
                "$project": {
                    "id": {"$toString": "$_id"},
                    "cost": 1,
                    "is_paid": 1,
                    "date": 1,
                    "contract": {
                        "id": {"$toString": "$contract_info._id"},
                        "start_date": "$contract_info.start_date",
                        "active": "$contract_info.active"
                    },
                    "_id": 0
                }
            }
        ]

        results = list(payments_coll.aggregate(pipeline))
        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
