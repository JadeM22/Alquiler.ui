import os
import logging
import requests
import bcrypt
import firebase_admin
import base64
import json
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException, Request
from bson import ObjectId
from dotenv import load_dotenv
from utils.mongodb import get_collection
from utils.security import create_jwt_token
from models.users import User, UserCreate, UserUpdate
from models.login import Login

# --- Configuración Firebase ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
coll = get_collection("users")

def initialize_firebase():
    if firebase_admin._apps:  # Nota el guion bajo
        return

    try:
        firebase_creds_base64 = os.getenv("FIREBASE_CREDENTIALS_BASE64")

        if firebase_creds_base64:
            firebase_creds_json = base64.b64decode(firebase_creds_base64).decode('utf-8')
            firebase_creds = json.loads(firebase_creds_json)
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized with environment variable credentials")

        else:
            cred = credentials.Certificate("secrets/alquiler-secret.json")
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized with JSON file")

    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise HTTPException(status_code=500, detail=f"Firebase configuration error: {str(e)}")

initialize_firebase()

# Crear nuevo usuario 
async def create_user_public(user: UserCreate) -> User:
    """Crea un usuario público (no admin) en Firebase y MongoDB."""
    try:
        # Verificar si el email ya existe
        if coll.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="El email ya está registrado")

        # Crear usuario en Firebase
        try:
            firebase_user = firebase_auth.create_user(
                email=user.email,
                password=user.password
            )
            firebase_uid = firebase_user.uid
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Firebase error: {e}")

        # Preparar documento para MongoDB (excluyendo id y password)
        user_dict = user.model_dump(exclude={"id", "password"})
        user_dict["firebase_uid"] = firebase_uid
        user_dict["admin"] = False  # Todos los usuarios públicos no son admin

        inserted = coll.insert_one(user_dict)

        # Retornar User sin password
        return User(
            id=str(inserted.inserted_id),
            full_name=user.full_name,
            email=user.email,
            active=user.active,
            admin=False
        )

    except HTTPException:
        raise
    except Exception as e:
        # Si algo falla después de crear el usuario en Firebase, eliminarlo
        if 'firebase_uid' in locals():
            try:
                firebase_auth.delete_user(firebase_uid)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Error creando usuario: {e}")

# Login de usuario
async def login(user: Login) -> dict:
    api_key = os.getenv("FIREBASE_API_KEY")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": user.email,
        "password": user.password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    response_data = response.json()

    if "error" in response_data:
        raise HTTPException(
            status_code=400,
            detail="Error al autenticar usuario"
        )

    coll = get_collection("users")
    user_info = coll.find_one({"email": user.email})

    if not user_info:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado en la base de datos"
        )

    return {
        "message": "Usuario autenticado correctamente",
        "idToken": create_jwt_token(
            user_info.get("full_name", "Usuario"),
            user_info.get("email"),
            user_info.get("active", True),
            user_info.get("admin", True),
            str(user_info["_id"])
        )
    }


# Lista un usuario en especifico
async def get_user_by_id_admin(request: Request, user_id: str) -> User:
    """Obtiene los datos de un usuario (solo administradores)."""
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(status_code=403, detail="Solo administradores pueden consultar usuarios")

        doc = coll.find_one({"_id": ObjectId(user_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        doc["id"] = str(doc["_id"])
        del doc["_id"]
        return User(**doc)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo usuario: {str(e)}")


# Actualizar perfil del usuario autenticado 
async def update_user_profile(request: Request, user_update: UserUpdate) -> User:
    """Actualiza los datos de un usuario (admin todos, usuario solo los suyos)."""
    try:
        user_id = request.state.id  # ID desde JWT
        existing = coll.find_one({"_id": ObjectId(user_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        update_data = user_update.model_dump(exclude_unset=True, exclude={"id", "admin"})

        #  Si hay password, actualizar en Firebase y en Mongo 
        if "password" in update_data and update_data["password"]:
            try:
                # Actualiza en Firebase si tienes el UID guardado
                if existing.get("firebase_uid"):
                    firebase_auth.update_user(existing["firebase_uid"], password=update_data["password"])
            except Exception as e:
                logger.warning(f"No se pudo actualizar la contraseña en Firebase: {e}")

            # Hashear y guardar en Mongo
            hashed = bcrypt.hashpw(update_data["password"].encode("utf-8"), bcrypt.gensalt())
            update_data["password"] = hashed.decode("utf-8")  # Guardar hasheada

        # Actualizar en Mongo
        if update_data:
            coll.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

        # Retornar usuario actualizado 
        updated = coll.find_one({"_id": ObjectId(user_id)})
        updated["id"] = str(updated["_id"])
        del updated["_id"]
        return User(**updated)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando perfil: {str(e)}")

