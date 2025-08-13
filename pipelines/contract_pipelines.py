"""
Pipelines de MongoDB para operaciones con contratos
"""
from bson import ObjectId

def get_contract_with_apartment_pipeline(contract_id: str) -> list:
    """
    Pipeline para obtener un contrato con información del apartamento relacionado
    """
    return [
        {"$match": {"_id": ObjectId(contract_id)}},
        {"$addFields": {
            "id_apartment_obj": {"$toObjectId": "$id_apartment"}
        }},
        {"$lookup": {
            "from": "apartments",
            "localField": "id_apartment_obj",
            "foreignField": "_id",
            "as": "apartment"
        }},
        {"$unwind": "$apartment"},
        {"$project": {
            "id": {"$toString": "$_id"},
            "id_user": {"$toString": "$id_user"},
            "tipo": "$apartment.number",  # Número del apartamento
            "start_date": "$start_date",
            "end_date": "$end_date",
            "status": "$status"
        }}
    ]

def get_all_contracts_with_apartments_pipeline(skip: int = 0, limit: int = 10) -> list:
    """
    Pipeline para obtener todos los contratos con información del apartamento relacionado
    """
    return [
        {"$addFields": {
            "id_apartment_obj": {"$toObjectId": "$id_apartment"}
        }},
        {"$lookup": {
            "from": "apartments",
            "localField": "id_apartment_obj",
            "foreignField": "_id",
            "as": "apartment"
        }},
        {"$unwind": "$apartment"},
        {"$project": {
            "_id": 0,
            "id": {"$toString": "$_id"},
            "id_user": {"$toString": "$id_user"},
            "tipo": "$apartment.number",
            "start_date": "$start_date",
            "end_date": "$end_date",
            "status": "$status"
        }},
        {"$skip": skip},
        {"$limit": limit}
    ]

def validate_contract_has_apartments_pipeline(contract_id: str) -> list:
    """
    Pipeline para validar si un contrato tiene apartamentos asignados
    """
    return [
        {"$match": {"_id": ObjectId(contract_id)}},
        {"$addFields": {
            "id_apartment_obj": {"$toObjectId": "$id_apartment"}
        }},
        {"$lookup": {
            "from": "apartments",
            "localField": "id_apartment_obj",
            "foreignField": "_id",
            "as": "apartments"
        }},
        {"$group": {
            "_id": {
                "id": {"$toString": "$_id"},
                "id_user": "$id_user",
                "status": "$status"
            },
            "number_of_apartments": {"$sum": {"$size": "$apartments"}}
        }},
        {"$project": {
            "_id": 0,
            "id": "$_id.id",
            "id_user": "$_id.id_user",
            "status": "$_id.status",
            "number_of_apartments": 1
        }}
    ]

def search_contracts_pipeline(search_term: str, skip: int = 0, limit: int = 10) -> list:
    """
    Pipeline para buscar contratos por id_user o apartamento relacionado
    """
    return [
        {"$addFields": {
            "id_apartment_obj": {"$toObjectId": "$id_apartment"}
        }},
        {"$lookup": {
            "from": "apartments",
            "localField": "id_apartment_obj",
            "foreignField": "_id",
            "as": "apartment"
        }},
        {"$unwind": "$apartment"},
        {"$match": {
            "$or": [
                {"id_user": {"$regex": search_term, "$options": "i"}},
                {"apartment.number": {"$regex": search_term, "$options": "i"}}
            ]
        }},
        {"$project": {
            "id": {"$toString": "$_id"},
            "id_user": {"$toString": "$id_user"},
            "tipo": "$apartment.number",
            "start_date": "$start_date",
            "end_date": "$end_date",
            "status": "$status"
        }},
        {"$skip": skip},
        {"$limit": limit}
    ]
