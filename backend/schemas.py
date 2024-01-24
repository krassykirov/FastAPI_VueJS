from pydantic import BaseModel
import datetime
from typing import List, Optional, Dict, Any
from models import Item, Category
import decimal

class CategoryCreate(BaseModel):
    name: str
    class Config:
        orm_mode = True
        schema_extra = {
        "example": {
            "name": "Category-Name",
           }
        }

class CategoryRead(BaseModel):
    name: str
    id:   Optional[int]
    # items: Optional[List[Item]]
    class Config:
        orm_mode = True
        schema_extra = {
        "example": {
            "id": 1,
            "name": "Category-Name",
           }
        }

class CategoryItems(BaseModel):
    id:   Optional[int]
    name: str
    items: Optional[List[Item]]
    class Config:
        orm_mode = True

class ItemRead(BaseModel):
    id:   Optional[int]
    name: Optional[str]
    date: Optional[datetime.datetime]
    price: Optional[decimal.Decimal]
    image: Optional[str]
    username: Optional[str]
    reviews: Optional[List]
    description:  Optional[str]
    category:  Optional[Category]
    category_id:  Optional[int]
    in_cart: Optional[Dict[Any,Any]]
    liked: Optional[Dict[Any,Any]]
    discount: Optional[decimal.Decimal]
    discount_price: Optional[decimal.Decimal]
    quantity: Optional[int]
    class Config:
        orm_mode = True
        schema_extra = {
        "example": {
            "id":1,
            "name": "Item-Name",
            "price": 99.99,
            "date": "2023-11-22 13:50:51",
            "image": "image.pgn",
            "username": "Krassy",
            "description": "description",
            'in_cart': "false",
            'liked': "false",
            'discount': 0.2,
            'discount_price': '1009.11',
            'quantity': 1
           }
        }

class ItemUpdate(BaseModel):
    name: Optional[str]
    class Config:
        orm_mode = True
        schema_extra = {
        "example": {
            "id":1,
            "name": "Item-Name",
            "price": 99.99,
            "date": "2023-11-22 13:50:51",
            "image": "image.pgn",
            "username": "Krassy",
            "description": "description",
            'in_cart': "false",
            'discount': 0.2,
            'discount_price': '1009.11',
            'quantity': 1
         }
     }
class ItemCreate(BaseModel):
    name: Optional[str]
    price: Optional[decimal.Decimal]
    description:  Optional[str]
    username: Optional[str]
    class Config:
        orm_mode = True
        schema_extra = {
        "example": {
            "name": "Item-Name",
            "price": 99.99,
            "description": "description"
           }
        }

class UserProfileUpdate(BaseModel):
    email:   Optional[str]
    primary_email: Optional[str]
    number:  Optional[str]
    address: Optional[str]
    class Config:
        orm_mode = True
        schema_extra = {
        "example": {
            "email": "krassy@mail.bg",
            "number": "0887194455",
            "address": "address"
           }
        }