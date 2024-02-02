from fastapi import FastAPI
from app.routers import product, orders
from dotenv import load_dotenv
from app.encoders import custom_json_encoder
import os

load_dotenv()

app = FastAPI()

app.include_router(product.router)
app.include_router(orders.router)

app.json_encoder = custom_json_encoder
