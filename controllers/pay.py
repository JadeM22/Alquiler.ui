from models.pay import Pay
from utils.mongodb import get_collection
from fastapi import HTTPException, Request
from bson import ObjectId

coll = get_collection("pays")
contracts_coll = get_collection("contracts")

# ---------------- Función auxiliar ----------------
def verify_pay_ownership(pay_doc, user_id: str) -> bool:
    """Verifica si el pago pertenece al usuario propietario del contrato."""
    contract_id = pay_doc.get("id_Contract")
    if not contract_id:
        return False
    try:
        oid_contract = ObjectId(contract_id)
    except Exception:
        oid_contract = None

    contract = contracts_coll.find_one({"_id": oid_contract or contract_id})
    if not contract:
        return False
    return str(contract.get("id_User")) == str(user_id)

# ---------------- CRUD ----------------
async def get_Pay(request: Request, contract_id: str) -> list[Pay]:
    """Obtiene todos los pagos de un contrato (admin ve todos, usuario solo los suyos)."""
    try:
        user_id = str(request.state.id)
        admin = getattr(request.state, "admin", False)
        payments = []

        try:
            oid_contract = ObjectId(contract_id)
        except:
            oid_contract = None

        contract = contracts_coll.find_one({"_id": oid_contract or contract_id})
        if not contract:
            raise HTTPException(404, "Contract not found")

        if not admin and str(contract.get("id_User")) != user_id:
            raise HTTPException(403, "Not authorized")

        query = {"id_Contract": contract_id}
        if oid_contract:
            query = {"$or": [{"id_Contract": contract_id}, {"id_Contract": oid_contract}]}

        for doc in coll.find(query):
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            payments.append(Pay(**doc))
        return payments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error getting payments: {e}")

async def get_Pay_by_id_contract(request: Request, contract_id: str, pay_id: str) -> Pay:
    """Obtiene un pago específico asociado a un contrato."""
    try:
        user_id = str(request.state.id)
        admin = getattr(request.state, "admin", False)

        oid_pay = ObjectId(pay_id)
        try:
            oid_contract = ObjectId(contract_id)
        except:
            oid_contract = None

        query = {
            "_id": oid_pay,
            "$or": [{"id_Contract": contract_id}]
        }
        if oid_contract:
            query["$or"].append({"id_Contract": oid_contract})

        doc = coll.find_one(query)
        if not doc:
            raise HTTPException(404, "Payment not found")
        if not admin and not verify_pay_ownership(doc, user_id):
            raise HTTPException(403, "Not authorized")

        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return Pay(**doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error getting payment: {e}")

async def create_pay(request: Request, contract_id: str, pay: Pay) -> Pay:
    """Crea un nuevo pago (solo administradores)."""
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(403, "Only admins can create payments")

        contract = contracts_coll.find_one({"_id": ObjectId(contract_id)})
        if not contract:
            raise HTTPException(404, "Contract not found")

        data = pay.model_dump(exclude={"id"})
        data["id_Contract"] = contract_id  # Asignamos relación con contrato

        res = coll.insert_one(data)
        data["id"] = str(res.inserted_id)
        return Pay(**data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error creating payment: {e}")

async def update_Pay(request: Request, pay_id: str, pay: Pay) -> Pay:
    """Actualiza un pago (solo administradores)."""
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(403, "Only admins can update payments")

        oid = ObjectId(pay_id)
        data = pay.model_dump(exclude={"id"})

        if coll.update_one({"_id": oid}, {"$set": data}).matched_count == 0:
            raise HTTPException(404, "Payment not found")

        doc = coll.find_one({"_id": oid})
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return Pay(**doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error updating payment: {e}")

# ---------------- PIPELINES ----------------
async def get_pays_with_contract_details(request: Request, contract_id: str):
    user_id = str(request.state.id)
    admin = getattr(request.state, "admin", False)

    # Convertimos el contract_id a ObjectId solo para buscar el contrato
    try:
        oid_contract = ObjectId(contract_id)
    except:
        oid_contract = None

    # Buscar contrato y validar permisos
    contract = contracts_coll.find_one({"_id": oid_contract})
    if not contract:
        raise HTTPException(404, "Contrato no encontrado")
    if not admin and str(contract.get("id_User")) != user_id:
        raise HTTPException(403, "No autorizado")

   
    # Convertir solo para buscar contrato
    try:
        oid_contract = ObjectId(contract_id)
    except:
        oid_contract = None

    # Verificar contrato y permisos
    contract = contracts_coll.find_one({"_id": oid_contract})
    if not contract:
        raise HTTPException(404, "Contrato no encontrado")
    if not admin and str(contract.get("id_User")) != user_id:
        raise HTTPException(403, "No autorizado")

    pipeline = [
        {
            "$match": {
                "$or": [
                    {"id_Contract": contract_id},
                    {"contract_id": contract_id}
                ]
            }
        },
        {
            "$lookup": {
                "from": "contracts",
                "let": {"cid1": "$id_Contract", "cid2": "$contract_id"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$or": [
                                    {"$eq": ["$_id", {"$toObjectId": "$$cid1"}]},
                                    {"$eq": ["$_id", {"$toObjectId": "$$cid2"}]}
                                ]
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
                "_id": 0,  # 🔥 eliminamos el _id original
                "id": {"$toString": "$_id"},  # id del pago
                "cost": 1,
                "is_paid": 1,
                "date": 1,
                # 🔥 convertimos id_Contract también
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

    results = list(coll.aggregate(pipeline))
    return results



async def get_pay_stats_by_contract(request: Request, contract_id: str):
    """Pipeline con $group para sumar y promediar pagos de un contrato."""
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

async def get_pays_pending_validation(request: Request):
    """Pipeline que devuelve pagos pendientes o contratos inactivos."""
    pipeline = [
        {
            "$lookup": {
                "from": "contracts",
                "let": {"cid": "$id_Contract"},   # 🔥 usamos el campo correcto
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {"$eq": ["$_id", {"$toObjectId": "$$cid"}]}
                        }
                    }
                ],
                "as": "contract_info"
            }
        },
        {"$unwind": "$contract_info"},
        {
            "$match": {
                "$or": [
                    {"is_paid": False},
                    {"contract_info.active": False}
                ]
            }
        },
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


async def get_pays_public(status: str | None = None, limit: int = 10, skip: int = 0):
    """Endpoint público con filtros y paginación."""
    query = {"is_paid": status.lower() == "true"} if status else {}
    cursor = coll.find(query).skip(skip).limit(limit)

    result = []
    for doc in cursor:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        result.append(doc)
    return result
