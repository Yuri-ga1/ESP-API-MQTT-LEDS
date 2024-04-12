from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from .schemas import Device
from database import database

router = APIRouter()


@router.post("/register_new_device")
async def register_device(device: Device):
    if not await database.is_user_exists(device.owner):
        RedirectResponse(url="/create_user")

    await database.register_device(device)
    return {"message": "New device has been successfully registered"}
