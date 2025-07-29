import os
import secrets
import hashlib
import base64
import jwt

from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from jwt import PyJWTError
from functools import wraps

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
security = HTTPBearer()

# Función para crear un JWT
def create_jwt_token(
        full_name:str
        , email: str
        , active: bool
        , admin: bool
        , id: str
):
    expiration = datetime.utcnow() + timedelta(hours=1)  # El token expira en 1 hora
    token = jwt.encode(
        {
            "id": id,
            "full_name": full_name,
            "email": email,
            "active": active,
            "admin": admin,
            "exp": expiration,
            "iat": datetime.utcnow()
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    return token

def validateuser(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=400, detail="Authorization header missing")

        schema, token = authorization.split()
        if schema.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid auth schema")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            email = payload.get("email")
            full_name = payload.get("full_name")
            active = payload.get("active")
            exp = payload.get("exp")
            user_id = payload.get("id")
            admin = payload.get("admin", False)  # ✅ extraer admin del token

            if email is None:
                raise HTTPException(status_code=401, detail="Token Invalid")

            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Expired token")

            if not active:
                raise HTTPException(status_code=401, detail="Inactive user")

            # ✅ guardar en request.state
            request.state.email = email
            request.state.full_name = full_name
            request.state.id = user_id
            request.state.admin = admin  # ✅ ahora se asigna correctamente

        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token or expired token")

        return await func(*args, **kwargs)
    return wrapper


def validateadmin(func):
    @wraps(func)
    async def wrapper( *args, **kwargs ):
        request = kwargs.get('request')
        if not request:
            raise HTTPException( status_code=400, detail="Request object not found"  )

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException( status_code=400, detail="Authorization header missing"  )

        schema, token = authorization.split()
        if schema.lower() != "bearer":
            raise HTTPException( status_code=400, detail="Invalid auth schema"  )

        try:
            payload = jwt.decode( token , SECRET_KEY, algorithms=["HS256"] )

            email = payload.get("email")
            full_name = payload.get("full_name")
            active = payload.get("active")
            admin = payload.get("admin")
            exp = payload.get("exp")
            id = payload.get("id")

            if email is None:
                raise HTTPException( status_code=401 , detail="Token Invalid" )

            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException( status_code=401 , detail="Expired token" )

            if not active or not admin:
                raise HTTPException( status_code=401 , detail="Inactive user or not admin" )

            request.state.email = email
            request.state.full_name = full_name
            request.state.admin = admin
            request.state.id = id


        except PyJWTError:
            raise HTTPException( status_code=401, detail="Invalid token or expired token"  )

        return await func( *args, **kwargs )
    return wrapper


# Funciones para FastAPI Dependency Injection
def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Validar token JWT para usuarios autenticados - Para usar con Depends()"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        email = payload.get("email")
        full_name = payload.get("full_name")
        active = payload.get("active")
        admin = payload.get("admin", False)
        exp = payload.get("exp")
        user_id = payload.get("id")
        
        if email is None:
            raise HTTPException(status_code=401, detail="Token Invalid")
        
        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Expired token")
        
        if not active:
            raise HTTPException(status_code=401, detail="Inactive user")
        
        return {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "active": active,
            "role": "admin" if admin else "user"
        }
        
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")


def validate_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Validar token JWT para administradores - Para usar con Depends()"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        email = payload.get("email")
        full_name = payload.get("full_name")
        active = payload.get("active")
        admin = payload.get("admin", False)
        exp = payload.get("exp")
        user_id = payload.get("id")
        
        if email is None:
            raise HTTPException(status_code=401, detail="Token Invalid")
        
        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Expired token")
        
        if not active or not admin:
            raise HTTPException(status_code=401, detail="Inactive user or not admin")
        
        return {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "active": active,
            "role": "admin"
        }
        
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")
    