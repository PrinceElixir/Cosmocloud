from typing import List
from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int

class CreateOrderRequest(BaseModel):
    items: List[ProductCreate]
    user_address: dict 
