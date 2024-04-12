from fastapi import FastAPI, HTTPException
from database import database
import uvicorn
import asyncio
from colors.router import router as colors_router
from device.router import router as device_router
from users.router import router as users_router


app = FastAPI()


app.include_router(colors_router)
app.include_router(device_router)
app.include_router(users_router)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def get_data():
    return {'message': 'Hello, world'}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)