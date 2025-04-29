from pydantic import BaseModel
from typing import Dict

class ItemInfo(BaseModel):
    price: int
    quantity: int
    category:str

LootResponse = Dict[str, ItemInfo]
