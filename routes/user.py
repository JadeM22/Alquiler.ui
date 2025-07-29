from fastapi import APIRouter, Request
from utils.security import validateuser, validateadmin
from models.users import User, UserCreate, UserUpdate
from models.login import Login
from controllers.users import (
    create_user_admin,
    login,
    get_user_by_id_admin,
    update_user_profile
)

router = APIRouter()


@router.post("/users", response_model=User)
@validateadmin
async def create_user_endpoint(request: Request, user: UserCreate):
    return await create_user_admin(request, user)


@router.post("/login")
async def login_endpoint(user: Login):
    return await login(user)


@router.get("/users/{user_id}", response_model=User)
@validateadmin
async def get_user_endpoint(request: Request, user_id: str):
    return await get_user_by_id_admin(request, user_id)


@router.put("/users", response_model=User)
@validateuser
async def update_user_endpoint(request: Request, user: UserUpdate):
    return await update_user_profile(request, user)

