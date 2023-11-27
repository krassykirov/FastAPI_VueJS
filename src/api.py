from fastapi import (
    Depends,
    HTTPException,
    Request,
    APIRouter,
    status,
    Form,
    BackgroundTasks )
from fastapi.responses import RedirectResponse
from src.db import get_session
from sqlalchemy.orm import Session
from sqlalchemy import select
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlmodel import SQLModel, Session
from src.db import engine
from src.routers.categories import category_router
from src.routers.items import items_router
from src.routers.reviews import reviews_router
from src.models import Item, Category, Review, User, UserRead
from src.crud.crud import CategoryActions, ItemActions, ReviewActions
# from src.auth.oauth import logout, login, login_access_token
from src.helper import delete_item_dir
import src.schemas
import json, os, shutil
from os.path import abspath
import decimal
from src.auth.oauth import oauth_router, get_current_user
from src.my_logger import detailed_logger


PROJECT_ROOT = Path(__file__).parent.parent

templates = Jinja2Templates(directory="src/static/templates")

app = FastAPI()
app.include_router(category_router)
app.include_router(items_router)
app.include_router(reviews_router)
app.include_router(oauth_router)

logger = detailed_logger()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/", include_in_schema=False)
async def home(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("base.html", {"request": request, 'current_user': user.username})

@app.post("/create_category", status_code=status.HTTP_201_CREATED, response_model=Category, include_in_schema=False)
async def create_cat(request: Request, name: str, db: Session = Depends(get_session), user: User = Depends(get_current_user)):
    """ Create category """
    form_data = await request.form()
    c = CategoryActions().get_category_by_name(db=db, name=form_data.get('name'))
    if c is not None:
        logger.error(f"Category with name:'{c.name}' already exist")
        raise HTTPException(status_code=404, detail=f"Category with name:'{c.name}' already exist")
    category = CategoryActions().create_category(db=db, category=Category(name=form_data.get('name')))
    return  templates.TemplateResponse("base.html", {"request":request, 'category': category})

@app.get("/details", include_in_schema=False)
@app.get("/items/details", response_model=src.schemas.ItemRead)
def get_details(request: Request, db: Session = Depends(get_session), user: User = Depends(get_current_user)):
    """ Return all Items """
    items_db = ItemActions().get_items(db=db) #, user=user.username
    items = [src.schemas.ItemRead.from_orm(item) for item in items_db]
    return templates.TemplateResponse("items.html", {"request": request, 'items': items, 'current_user': user.username})

@app.post("/create_item", include_in_schema=False)
@app.post("/items/create_item", include_in_schema=False)
async def create_item(request: Request, db: Session = Depends(get_session), user: User = Depends(get_current_user)):
        """ Create an Item """
        form_data = await request.form()
        file = form_data['file']
        filename = form_data['file'].filename
        item_name =form_data['name']
        price=form_data['price']
        query = db.query(Item).where(Item.name == item_name).all()
        item = [item for item in query]
        items = ItemActions().get_items(db=db)
        if item:
            logger.error(f"item with that name already exists!")
            return templates.TemplateResponse("items.html", {"request":request, 'items':items,
                                                                   'message': "Item with that name already exists!"})
            # redirect_url = request.url_for('get_details')
            # response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
            # return response
        IMG_DIR = os.path.join(PROJECT_ROOT, f'src/static/img/{user.username}')
        content = await file.read()
        path = os.path.join(IMG_DIR, item_name)
        if not os.path.exists(path):
               os.makedirs(path,exist_ok=True)
        with open(f"src/static/img/{user.username}/{item_name}/{filename}", 'wb') as f:
            f.write(content)
            item = Item(name=item_name, price=price, image=filename, username=user.username)
        db.add(item)
        db.commit()
        redirect_url = request.url_for('get_details')
        response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
        return response

@app.post("/delete_item", include_in_schema=False)
@app.post("/items/delete_item")
async def delete_item(request: Request, background_tasks: BackgroundTasks, id: int=Form(None), db: Session=Depends(get_session),
                      user: User = Depends(get_current_user))-> None:
     item = ItemActions().get_item_by_id(db=db, id=id)
     if item:
        db.delete(item)
        db.commit()
        try:
            dir_to_delete = abspath(f"src/static/img/{user.username}/{item.name}/")
            background_tasks.add_task(delete_item_dir, path=dir_to_delete)
            logger.info("Notification sent in the background")
            redirect_url = request.url_for('get_details')
            response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
            return response
        except Exception as e:
            logger.error(f"Something went wrong, error: {e}")
            return HTTPException(status_code=400, detail=f"Something went wrong, error {e}")
     else:
        raise HTTPException(status_code=404,detail=f"No item with id={id}")

@app.get("/items/{id}", response_model=src.schemas.ItemRead, include_in_schema=False) # http://127.0.0.1:8000/api/items?name=12
async def read_item(request: Request, id: int, db: Session=Depends(get_session), user: User = Depends(get_current_user)):
    item_db = ItemActions().get_item_by_id(db=db, id=id)
    item = src.schemas.ItemRead.from_orm(item_db)
    item_rating = ReviewActions().get_item_reviews_rating(db=db,id=id)
    logger.info('item_rating', item_rating)
    return templates.TemplateResponse("item_details.html", {"request":request, 'item': item,
                                                             'current_user': user.username,
                                                             'rating' : item_rating})

@app.post("/update_price_ajax", include_in_schema=False, response_model=src.schemas.ItemRead)
async def update_item_api(request: Request, db: Session=Depends(get_session)) -> src.schemas.ItemRead:
    data = await request.json()
    logger.info('data', data)
    item = ItemActions().get_item_by_id(db=db, id=data.get('id'))
    if not item:
        logger.error("Item not found")
        raise HTTPException(status_code=404, detail="Item not found")
    new_data = Item(**data).dict(exclude_unset=True, exclude_none=True)
    for key, value in new_data.items():
        setattr(item, key, value)
        db.commit()
        db.refresh(item)
    return item

@app.post("/update_description_ajax", status_code=status.HTTP_200_OK, response_model=src.schemas.ItemRead, include_in_schema=False)
async def update_description_ajax(request: Request, db: Session=Depends(get_session)) -> src.schemas.ItemRead:
    data = await request.json()
    item = ItemActions().get_item_by_id(db=db, id=data.get('id'))
    if not item:
        logger.error("Item not found")
        raise HTTPException(status_code=404, detail="Item not found")
    new_data = Item(**data).dict(exclude_unset=True, exclude_none=True)
    for key, value in new_data.items():
        setattr(item, key, value)
        db.commit()
        db.refresh(item)
    return item

@app.post("/create_review_ajax", status_code=status.HTTP_200_OK, response_model=Review, include_in_schema=False)
async def create_review_ajax(request: Request, db: Session=Depends(get_session), user: User = Depends(get_current_user)) -> Review:
    data = await request.json()
    item = ItemActions().get_item_by_id(db=db, id=data.get('item_id'))
    if not item:
        logger.error("Item not found")
        raise HTTPException(status_code=404, detail="Item not found")
    review = Review(**data, item=item)
    logger.info(f"Creating review {review}")
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

@app.get("/user/items", response_model=src.schemas.ItemRead, include_in_schema=False)
async def get_user_items( request: Request, db: Session=Depends(get_session), user: User = Depends(get_current_user)):
    items = ItemActions().get_items(db=db, user=user.username)
    return templates.TemplateResponse("items.html", {"request":request, 'items':items, 'current_user': user.username})


app.mount("/static", StaticFiles(directory="src/static", html=True))