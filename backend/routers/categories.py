from fastapi import APIRouter, status
from fastapi import Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from db.database_factory import get_session
from sqlalchemy.orm import Session
from crud.crud import CategoryActions
from schemas import CategoryCreate, CategoryItems, CategoryRead
from models import Category, Categories
from auth.oauth import get_current_user
from my_logger import detailed_logger

# PROTECTED = [Depends(get_current_user)]

category_router = APIRouter(prefix='/api/categories', tags=["categories"],
                            responses={404: {"description": "Not found"}},)

logger = detailed_logger()

@category_router.get("/", status_code=status.HTTP_200_OK)
def get_categories_items_len(request: Request, db: Session = Depends(get_session)):
    """ Return all items in a category """
    categories = CategoryActions().get_categories_len(db=db)
    if categories is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No categories found")
    return JSONResponse(content=jsonable_encoder(categories))

@category_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=CategoryRead)
def get_category_by_id(request: Request, id: int, db: Session = Depends(get_session)):
    """ Return category by given id"""
    category = CategoryActions().get_category_by_id(db=db, id=id)
    if category is None:
        raise HTTPException(status_code=404, detail=f"No category with id {id} found")
    return category


@category_router.get("/category_items/", status_code=status.HTTP_200_OK, response_model=CategoryItems)
def get_category_items(name: str, db: Session = Depends(get_session)):
    """ Return all items in a category """
    category = CategoryActions().get_category_by_name(db=db, name=name)
    if category is None:
        raise HTTPException(status_code=404, detail=f"No category  found for {name}")
    return category

@category_router.post("/", status_code=status.HTTP_201_CREATED, response_model=CategoryRead, include_in_schema=False)
def create_category(request: Request, category: CategoryCreate, db: Session = Depends(get_session)):
    """ Create category """
    c = CategoryActions().get_category_by_name(db=db, name=category.name)
    if c is not None:
        logger.info(f"Category with name:'{c.name}' already exist")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Category with name:'{c.name}' already exist")
    if category.name =='':
        logger.error(f"Category Name is required!")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Category Name is required!")
    try:
        category = CategoryActions().create_category(db=db, category=category)
        return category
    except Exception as e:
       logger.error(f"Error while creating Category, error message: {e}")


@category_router.delete("/{category_id}", include_in_schema=False, status_code=status.HTTP_204_NO_CONTENT)
def delete_category(request: Request, category_id: int, db: Session = Depends(get_session)):
    """ Delete category """
    category = CategoryActions().get_category_by_id(db=db, id=category_id)
    if category is None:
       logger.error(f"No category with id {category_id} found")
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No category with id {category_id} found")
    CategoryActions().delete_category(db=db, id=category_id)

