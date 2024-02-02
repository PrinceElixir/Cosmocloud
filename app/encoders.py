from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from json import JSONEncoder
from pydantic import BaseModel
from typing import Any, Dict

class CustomJSONEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, BaseModel):
            return o.dict()
        return super().default(o)

def custom_json_encoder(data: Any, *, include: Dict[str, Any] = {}) -> str:
    return CustomJSONEncoder().encode(data, include=include)
