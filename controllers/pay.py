from models.pay import Pay
from utils.mongodb import get_collection
from fastapi import HTTPException, Request
from bson import ObjectId

coll = get_collection("pays")
contracts_coll = get_collection("contracts")


# 🔹 Función auxiliar para validar propietario
def verify_pay_ownership(pay_doc, user_id: str) -> bool:
    """Verifica si el pago pertenece al usuario autenticado."""
    contract_id = pay_doc.get("contract_id") or pay_doc.get("id_Contract")
    if not contract_id:
        return False
    try:
        oid_contract = ObjectId(contract_id)
    except Exception:
        oid_contract = None

    contract = contracts_coll.find_one({"_id": oid_contract or contract_id})
    if not contract:
        return False
    
    contract_owner = str(contract.get("id_User") or contract.get("user_id") or "")
    return contract_owner == str(user_id)


# ✅ GET /contracts/{contract_id}/pay → Lista pagos de un contrato específico
async def get_Pay(request: Request, contract_id: str) -> list[Pay]:
    try:
        user_id = str(request.state.id)
        admin = getattr(request.state, "admin", False)
        payments = []

        print(f"DEBUG → user_id={user_id} | admin={admin} | contract_id={contract_id}")

        # ✅ Validar contract_id
        try:
            oid_contract = ObjectId(contract_id)
        except Exception:
            oid_contract = None

        # ✅ Verificar que el contrato exista
        contract = contracts_coll.find_one({"_id": oid_contract or contract_id})
        if not contract:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")

        # ✅ Validar propietario si no es admin
        owner_id = str(contract.get("id_User") or contract.get("user_id") or "")
        print(f"DEBUG → owner_id={owner_id}")
        if not admin and owner_id != user_id:
            raise HTTPException(status_code=403, detail="No autorizado para ver pagos de este contrato")

        # ✅ Buscar pagos del contrato por ambos campos y tipos
        query = {
            "$or": [
                {"contract_id": contract_id},
                {"id_Contract": contract_id}
            ]
        }
        if oid_contract:
            query["$or"] += [
                {"contract_id": oid_contract},
                {"id_Contract": oid_contract}
            ]

        print(f"DEBUG → Query pagos: {query}")
        cursor = coll.find(query)

        # ✅ Procesar pagos encontrados
        for doc in cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            payments.append(Pay(**doc))

        print(f"DEBUG → Pagos encontrados: {len(payments)}")
        return payments

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo pagos: {str(e)}")



# ✅ GET /contracts/{contract_id}/pays/{pay_id} → Ver un pago específico de un contrato
async def get_Pay_by_id_contract(request: Request, contract_id: str, pay_id: str) -> Pay:
    try:
        user_id = str(request.state.id)
        admin = getattr(request.state, "admin", False)

        try:
            oid_pay = ObjectId(pay_id)
        except Exception:
            raise HTTPException(status_code=400, detail="ID de pago inválido")

        try:
            oid_contract = ObjectId(contract_id)
        except Exception:
            oid_contract = None

        # 🔹 Filtro para buscar el pago con ambas variantes de campo
        query = {
            "_id": oid_pay,
            "$or": [
                {"contract_id": contract_id},
                {"id_Contract": contract_id}
            ]
        }
        if oid_contract:
            query["$or"] += [{"contract_id": oid_contract}, {"id_Contract": oid_contract}]

        doc = coll.find_one(query)
        if not doc:
            raise HTTPException(status_code=404, detail="Pago no encontrado")

        # 🔹 Si no es admin, verificar propietario del contrato
        if not admin and not verify_pay_ownership(doc, user_id):
            raise HTTPException(status_code=403, detail="No autorizado para ver este pago")

        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return Pay(**doc)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo pago: {str(e)}")


# ✅ POST /contracts/{contract_id}/pays → Crear pago (solo admin)
async def create_pay(request: Request, contract_id: str, pay: Pay) -> Pay:
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(status_code=403, detail="Solo administradores pueden crear pagos")

        contract = contracts_coll.find_one({"_id": ObjectId(contract_id)})
        if not contract:
            raise HTTPException(status_code=404, detail="Contrato no encontrado")

        pay_dict = pay.model_dump(exclude={"id"})
        pay_dict["contract_id"] = contract_id

        result = coll.insert_one(pay_dict)
        pay_dict["id"] = str(result.inserted_id)
        return Pay(**pay_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando pago: {str(e)}")


# ✅ PUT /pays/{pay_id} → Actualizar pago (solo admin)
async def update_Pay(request: Request, pay_id: str, pay: Pay) -> Pay:
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(status_code=403, detail="Solo administradores pueden actualizar pagos")

        oid_pay = ObjectId(pay_id)
        pay_dict = pay.model_dump(exclude={"id"})

        result = coll.update_one({"_id": oid_pay}, {"$set": pay_dict})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Pago no encontrado")

        updated_doc = coll.find_one({"_id": oid_pay})
        updated_doc["id"] = str(updated_doc["_id"])
        del updated_doc["_id"]

        return Pay(**updated_doc)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando pago: {str(e)}")


