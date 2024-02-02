import os
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongomock import MongoClient
from app.routers import product
from app.models import ProductModel
from dotenv import load_dotenv
import sys

print(sys.path)


load_dotenv()

app = FastAPI()
app.include_router(product.router)


mongodb_connection_string = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
product.router.products_collection = MongoClient.from_uri(mongodb_connection_string).db.products

client = TestClient(app)


def test_list_products():
    
    test_products = [
        {"_id": str(i), "name": f"Product {i}", "price": float(i * 100), "quantity": i * 2}
        for i in range(1, 21)  
    ]
    product.router.products_collection.insert_many(test_products)

    response = client.get("/products/")
    assert response.status_code == 200


    data = response.json()
    assert "data" in data
    assert "page" in data

 
    assert len(data["data"]) == len(test_products)

    for i, product_data in enumerate(data["data"]):
        assert isinstance(product_data, ProductModel)
        assert product_data.id == str(i + 1)
        assert product_data.name == f"Product {i + 1}"
        assert product_data.price == float((i + 1) * 100)
        assert product_data.quantity == (i + 1) * 2

    assert data["page"]["total"] == len(data["data"])

