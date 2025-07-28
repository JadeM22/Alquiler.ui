import os
import uvicorn
import logging

from fastapi import FastAPI, Request
from dotenv import load_dotenv

from utils.security import validateuser, validateadmin

from routes.Apartment import router as Apartment
from routes.contract import router as contract
from routes.maintenance_type import router as maintenance_type
from routes.maintenance import router as maintenance
from routes.pay import router as pay
from routes.user import router as user  # ✅ ya contiene /users y /login

app = FastAPI()

# --- Incluir routers ---
app.include_router(Apartment, tags=["🏢 Apartments"])
app.include_router(contract, tags=["📜 Contracts"])
app.include_router(maintenance_type, tags=["🛠️ Maintenance Types"])
app.include_router(maintenance, tags=["🧰 Maintenance"])
app.include_router(pay, tags=["💰 Payments"])
app.include_router(user, tags=["👥 Users"])

load_dotenv()

@app.get("/")
def read_root():
    return {"version": "0.0.0"}


# Endpoint solo para administradores
@app.get("/admin")
@validateadmin
async def admin(request: Request):
    return {
        "message": "Endpoint de administrador",
        "admin": request.state.admin  # La info del admin ya se guarda en request.state
    }


# Endpoint para usuarios autenticados
@app.get("/user")
@validateuser 
async def user_info(request: Request):
    return {
        "message": "Endpoint de usuario",
        "email": request.state.email  # El decorador ya puso el email en request.state
    }


# ----- Agregar configuración para que Swagger tenga botón Authorize -----
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="API con JWT y validación de roles con decoradores",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

