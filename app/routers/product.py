from fastapi import APIRouter, Query
from motor.motor_asyncio import AsyncIOMotorClient
from app.schemas import ProductCreate
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI", "")
mongo_client = AsyncIOMotorClient(mongo_uri)
mongo_db = mongo_client["myecommerceapp"]
products_collection = mongo_db["products"]

router = APIRouter()

@router.post("/products/")
async def create_product(product_data: ProductCreate):

    if not product_data.name or not product_data.price or not product_data.quantity:
        raise HTTPException(status_code=400, detail="Name, price, and quantity are required.")


    product_id = await products_collection.insert_one(product_data.dict())
    

    return {"id": str(product_id.inserted_id), **product_data.dict()}

@router.get("/products/")
async def list_products(
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0, ge=0),
    min_price: float = Query(default=None),
    max_price: float = Query(default=None),
):

    pipeline = [
        {"$match": {}},  
    ]

    
    if min_price is not None:
        pipeline.append({"$match": {"price": {"$gte": min_price}}})
    if max_price is not None:
        pipeline.append({"$match": {"price": {"$lte": max_price}}})

    
    pipeline.extend([
        {"$skip": offset},
        {"$limit": limit},
    ])

    
    count_pipeline = pipeline.copy()
    count_pipeline.extend([
        {"$count": "total"},
    ])

    
    products_cursor = products_collection.aggregate(pipeline)
    total_records_cursor = products_collection.aggregate(count_pipeline)

    
    products_data = await products_cursor.to_list(length=limit)
    total_records = await total_records_cursor.to_list(length=1)
    total = total_records[0]["total"] if total_records else 0

    
    next_offset = offset + limit if offset + limit < total else None
    prev_offset = offset - limit if offset - limit >= 0 else None

    
    response_data = {
        "data": products_data,
        "page": {
            "limit": limit,
            "nextOffset": next_offset,
            "prevOffset": prev_offset,
            "total": total,
        },
    }

    return response_data
