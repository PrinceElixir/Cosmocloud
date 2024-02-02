from fastapi import APIRouter, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from app.schemas import CreateOrderRequest
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI", "")
mongo_client = AsyncIOMotorClient(mongo_uri)
mongo_db = mongo_client["myecommerceapp"]
orders_collection = mongo_db["orders"]

router = APIRouter()

@router.post("/orders/")
async def create_order(order_request: CreateOrderRequest):
    
    if not order_request.items:
        raise HTTPException(status_code=400, detail="Items list cannot be empty.")

   
    order_id = await orders_collection.insert_one(order_request.dict())

    
    return {"id": str(order_id.inserted_id), **order_request.dict()}

@router.get("/orders/")
async def list_orders(
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0, ge=0),
    min_price: float = Query(default=None),
    max_price: float = Query(default=None),
):
    
    pipeline = [
        {"$skip": offset},
        {"$limit": limit},
    ]

    
    if min_price is not None:
        pipeline.append({"$match": {"total_amount": {"$gte": min_price}}})
    if max_price is not None:
        pipeline.append({"$match": {"total_amount": {"$lte": max_price}}})

    
    count_pipeline = pipeline.copy()
    count_pipeline.extend([
        {"$count": "total"},
    ])

    
    orders_cursor = orders_collection.aggregate(pipeline)
    total_records_cursor = orders_collection.aggregate(count_pipeline)

    
    orders_data = await orders_cursor.to_list(length=limit)
    total_records = await total_records_cursor.to_list(length=1)
    total = total_records[0]["total"] if total_records else 0

   
    next_offset = offset + limit if offset + limit < total else None
    prev_offset = offset - limit if offset - limit >= 0 else None

    
    response_data = {
        "data": orders_data,
        "page": {
            "limit": limit,
            "nextOffset": next_offset,
            "prevOffset": prev_offset,
            "total": total,
        },
    }

    return response_data
