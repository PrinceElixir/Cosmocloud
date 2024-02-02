from pydantic import BaseModel
from typing import List

class OrderItem(BaseModel):
    productId: str
    boughtQuantity: int

class UserAddress(BaseModel):
    City: str
    Country: str
    ZipCode: str

class CreateOrderRequest(BaseModel):
    items: List[OrderItem]
    userAddress: UserAddress
