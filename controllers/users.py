import os
import logging
import requests
import bcrypt
import firebase_admin
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

cred = credentials.Certificate("secrets/alquiler-secret.json")
firebase_admin.initialize_app(cred)

load_dotenv()
coll = get_collection("users")

# --- Crear nuevo usuario (solo admin) ---
async def create_user_admin(request: Request, user: UserCreate) -> User:
    try:
        if not getattr(request.state, "admin", False):
            raise HTTPException(status_code=403, detail="Solo administradores pueden crear usuarios")

        # Crear usuario en Firebase
        try:
            firebase_auth.create_user(email=user.email, password=user.password)
        except Exception as e:
            logger.warning(e)
            raise HTTPException(status_code=400, detail="Error al registrar usuario en Firebase")

        existing = coll.find_one({"email": user.email})
        if existing:
            raise HTTPException(status_code=400, detail="El email ya está registrado")

        user_dict = user.model_dump(exclude={"id", "password"})
        inserted = coll.insert_one(user_dict)
        user.id = str(inserted.inserted_id)
        return user

    except Exception as e:
        logger.error(f"Error creando usuario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creando usuario: {str(e)}")

# --- Login de usuario ---
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

# --- Obtener usuario por ID (solo admin) ---
async def get_user_by_id_admin(request: Request, user_id: str) -> User:
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

# --- Actualizar perfil del usuario autenticado ---
async def update_user_profile(request: Request, user_update: UserUpdate) -> User:
    try:
        user_id = request.state.id  # ID desde JWT
        existing = coll.find_one({"_id": ObjectId(user_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        update_data = user_update.model_dump(exclude_unset=True, exclude={"id", "admin"})

        # --- Si hay password, actualizar en Firebase y en Mongo ---
        if "password" in update_data and update_data["password"]:
            try:
                # 🔹 Actualiza en Firebase si tienes el UID guardado
                if existing.get("firebase_uid"):
                    firebase_auth.update_user(existing["firebase_uid"], password=update_data["password"])
            except Exception as e:
                logger.warning(f"No se pudo actualizar la contraseña en Firebase: {e}")

            # 🔹 Hashear y guardar en Mongo
            hashed = bcrypt.hashpw(update_data["password"].encode("utf-8"), bcrypt.gensalt())
            update_data["password"] = hashed.decode("utf-8")  # Guardar hasheada

        # --- Actualizar en Mongo ---
        if update_data:
            coll.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

        # --- Retornar usuario actualizado ---
        updated = coll.find_one({"_id": ObjectId(user_id)})
        updated["id"] = str(updated["_id"])
        del updated["_id"]
        return User(**updated)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando perfil: {str(e)}")

