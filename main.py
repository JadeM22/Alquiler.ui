import os
import uvicorn
from fastapi import FastAPI, Request
from dotenv import load_dotenv

from utils.security import validateuser, validateadmin

from routes.Apartment import router as Apartment
from routes.contract import router as contract
from routes.maintenance_type import router as maintenance_type
from routes.maintenance import router as maintenance
from routes.pay import router as pay
from routes.user import router as user

load_dotenv()

app = FastAPI()

# Add CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(Apartment)
app.include_router(contract, tags=["📜 Contracts"])
app.include_router(maintenance_type, tags=["🛠️ Maintenance Types"])
app.include_router(maintenance, tags=["🧰 Maintenance"])
app.include_router(pay)
app.include_router(user, prefix="/users", tags=["👥 Users"])


@app.get("/")
def read_root():
    return {"version": "0.0.0"}

@app.get("/health")
def health_check():
    try:
        return {
            "status": "healthy",
            "timestamp": "2025-08-06",
            "service": "alquiler-api",
            "environment": "production"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/ready")
def readiness_check():
    try:
        from utils.mongodb import test_connection
        db_status = test_connection()
        return {
            "status": "ready" if db_status else "not_ready",
            "database": "connected" if db_status else "disconnected",
            "service": "alquiler-api"
        }
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}

@app.get("/admin")
@validateadmin
async def admin_endpoint(request: Request):
    return {
        "message": "Endpoint de administrador",
        "admin": request.state.admin
    }

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
