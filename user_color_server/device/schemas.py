from pydantic import BaseModel

class Device(BaseModel):
    name: str
    mac: str
    owner: str