from fastapi import APIRouter
from .schemas import *
from database import database
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from typing import List
import random

router = APIRouter()


@router.post("/create_color")
async def create_color(color: Color):
    if not await database.is_user_exists(color.owner):
        RedirectResponse(url="/create_user")

    await database.add_new_color(color)
    return {"message": "New color has been successfully created"}


@router.post("/create_colors_combination")
async def create_colors_combination(colors_combination: Colors_combination):
    if len(colors_combination.colors) > 0:
        if not await database.is_user_exists(colors_combination.owner):
            RedirectResponse(url="/create_user")

        await database.create_colors_combination(colors_combination)

        return {"message": "Color combination has been successfully created"}

    return {
        "message": f"Your must add more then {len(colors_combination.colors)} colors"
    }


@router.post("/create_random_color")
async def random_color(owner: str):
    color = await generate_random_color(owner)
    await database.add_new_color(color)
    return {
        "message": f"New color has been successfully created with name: {color.name}"
    }


@router.get("/{username}_colors")
async def user_colors(username: str):
    user_colors = await database.get_user_colors(username)
    if not user_colors:
        raise HTTPException(status_code=404, detail=f"Users color not found")
    return user_colors


async def generate_random_color(owner: str) -> Color:
    color_name = "color_" + "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=5))
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    return Color(name=color_name, owner=owner, red=red, green=green, blue=blue)
