from fastapi import APIRouter, HTTPException
from utils.mongodb import get_collection

router = APIRouter()
payments_coll = get_collection("pays")  # 🔹 Unificado con 'pays'

@router.get("/payments/stats")
async def get_payments_stats():
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$contract_id",
                    "total_payments": {"$sum": 1},
                    "total_amount": {"$sum": "$cost"},
                    "avg_amount": {"$avg": "$cost"}
                }
            },
            {
                "$project": {
                    "contract_id": {"$toString": "$_id"},
                    "total_payments": 1,
                    "total_amount": 1,
                    "avg_amount": 1,
                    "_id": 0
                }
            }
        ]
        stats = list(payments_coll.aggregate(pipeline))
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")
