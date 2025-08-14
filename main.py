import uvicorn
import logging

from fastapi import FastAPI, Request

from controllers.users import create_user, login
from models.users import User
from models.login import Login

from utils.security import validateuser, validateadmin

from routes.Apartment import router as Apartment
from routes.contract import router as contract
from routes.maintenance_type import router as maintenance_type
from routes.maintenance import router as maintenance
from routes.pay import router as pay

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def read_root():
    return {"status": "healthy", "version": "0.0.0", "service": "administracio-Alquiler.api"}

@app.get("/health")
def health_check():
    try:
        return {
            "status": "healthy",
            "timestamp": "2025-08-06",
            "service": "administracion-Alquiler.api",
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
            "service": "administracion-Alquiler.api"
        }
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}

@app.post("/users")
async def create_user_endpoint(user: User) -> User:
    return await create_user(user)

@app.post("/login")
async def login_access(l: Login) -> dict:
    return await login(l)

@app.get("/exampleadmin")
@validateadmin
async def example_admin(request: Request):
    return {
        "message": "This is an example admin endpoint."
        , "admin": request.state.admin
    }

@app.get("/exampleuser")
@validateuser
async def example_user(request: Request):
    return {
        "message": "This is an example user endpoint."
        ,"email": request.state.email
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
