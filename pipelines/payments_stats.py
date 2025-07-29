from fastapi import HTTPException
from utils.mongodb import get_collection

payments_coll = get_collection("pays")


async def get_payments_stats_pipeline():
    """Pipeline que agrupa pagos y devuelve estadísticas por contrato."""
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
        return list(payments_coll.aggregate(pipeline))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando pipeline de estadísticas: {str(e)}")
