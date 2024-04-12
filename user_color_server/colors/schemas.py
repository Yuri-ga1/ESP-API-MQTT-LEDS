from pydantic import BaseModel
from typing import List


class Color(BaseModel):
    name: str
    owner: str
    red: int
    green: int
    blue: int


class Colors_combination(BaseModel):
    owner: str
    colors: List[str]
