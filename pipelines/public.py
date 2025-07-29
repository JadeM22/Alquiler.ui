from utils.mongodb import get_collection

coll = get_collection("apartments")

async def get_apartments_public(active: str | None = None, limit: int = 10, skip: int = 0):
    """Obtiene lista pública de apartamentos con filtros y paginación."""
    query = {"active": active.lower() == "true"} if active else {}
    cursor = coll.find(query).skip(skip).limit(limit)

    result = []
    for doc in cursor:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        result.append(doc)
    return result
