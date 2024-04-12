from fastapi import APIRouter
from .schemas import User
from database import database

router = APIRouter()


@router.post("/create_user")
async def create_user(user: User):
    await database.create_new_user(user)

    return {"message": "New user successfully created"}
