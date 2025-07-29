import os
import uvicorn
from fastapi import FastAPI, Request
from dotenv import load_dotenv

from utils.security import validateuser, validateadmin

# Importar routers
from routes.Apartment import router as Apartment
from routes.contract import router as contract
from routes.maintenance_type import router as maintenance_type
from routes.maintenance import router as maintenance
from routes.pay import router as pay
from routes.user import router as user
# Importar routers de pipelines
from pipelines.payments_stats import router as payments_stats_router
from pipelines.payments_enriched import router as payments_enriched_router
from pipelines.check_maintenance import router as check_maintenance_router
  # Contiene /users y /login

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Alquiler API")

# --- Incluir routers con tags ---
# --- Incluir routers con tags ---
app.include_router(Apartment, tags=["🏢 Apartments"])
app.include_router(contract, tags=["📜 Contracts"])
app.include_router(maintenance_type, tags=["🛠️ Maintenance Types"])
app.include_router(maintenance, tags=["🧰 Maintenance"])
app.include_router(pay, tags=["💰 Payments"])
app.include_router(user, tags=["👥 Users"])

# 🔹 Incluir pipelines como endpoints adicionales
app.include_router(payments_stats_router, tags=["📊 Pipeline: Stats"])
app.include_router(payments_enriched_router, tags=["🔗 Pipeline: Enriched"])
app.include_router(check_maintenance_router, tags=["🔍 Pipeline: Maintenance Check"])


# Ruta base simple
@app.get("/")
def read_root():
    return {"version": "0.0.0"}

# Endpoint protegido solo para administradores
@app.get("/admin")
@validateadmin
async def admin_endpoint(request: Request):
    return {
        "message": "Endpoint de administrador",
        "admin": request.state.admin
    }

# Endpoint protegido para usuarios autenticados
@app.get("/user")
@validateuser 
async def user_info_endpoint(request: Request):
    return {
        "message": "Endpoint de usuario",
        "email": request.state.email
    }

# ----- Configuración para que Swagger tenga botón Authorize -----
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
