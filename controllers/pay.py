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


# Lista los pagos 
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
            raise HTTPException(404, "Contrato no encontrado")

        if not admin and str(contract.get("id_User")) != user_id:
            raise HTTPException(403, "No autorizado")

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
        raise HTTPException(500, f"Error al recibir pagos: {e}")


# Lista un pago específico asociado a un contrato.
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
            raise HTTPException(403, "No autorizado")

        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return Pay(**doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error al recibir pagos: {e}")


#Crea un nuevo pago 
async def create_pay(request: Request, contract_id: str, pay: Pay) -> Pay:
    """Crea un nuevo pago (solo administradores)."""
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(403, "Solo administradores pueden crear pagos")

        contract = contracts_coll.find_one({"_id": ObjectId(contract_id)})
        if not contract:
            raise HTTPException(404, "Contrato no encontrado")

        data = pay.model_dump(exclude={"id"})
        data["id_Contract"] = contract_id  

        res = coll.insert_one(data)
        data["id"] = str(res.inserted_id)
        return Pay(**data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error creando pago: {e}")


# Actualiza un pago
async def update_Pay(request: Request, pay_id: str, pay: Pay) -> Pay:
    """Actualiza un pago (solo administradores)."""
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(403, "Solo administradores pueden actualizar pagos")

        oid = ObjectId(pay_id)
        data = pay.model_dump(exclude={"id"})

        if coll.update_one({"_id": oid}, {"$set": data}).matched_count == 0:
            raise HTTPException(404, "Pago no encontrado")

        doc = coll.find_one({"_id": oid})
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return Pay(**doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error actualizando pago {e}")

