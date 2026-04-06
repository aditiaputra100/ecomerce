from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from app.database import get_db
from app.schemas import ProductShop, success_response
from app.products.service import get_products
from . import schemas, models, service, utils, dependencies

auth = APIRouter(prefix="", tags=["Authentication"])
user = APIRouter(prefix="", tags=["User"])

@auth.post("/register")
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        disable=user_data.disable,
        db=db
    )
    # Convert to Pydantic schema to avoid exposing sensitive fields
    user_response = schemas.User.model_validate(new_user)
    return success_response(data=user_response, status_code=201)

@auth.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_obj = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user_obj or not utils.verify_password(form_data.password, user_obj.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    scopes = service.compute_scopes_for_user(user_obj)
    access_token = utils.create_access_token(data={"sub": user_obj.username, "scopes": " ".join(scopes)})
    token_data = {"access_token": access_token, "token_type": "bearer"}
    return success_response(data=token_data)

@user.get("/user/me")
def get_information_user(current_user: Annotated[models.User, Depends(dependencies.get_current_active_user)]):
    return success_response(data=schemas.User.model_validate(current_user))

@user.get("/{username}/products")
def get_username_catalog(username: str, db: Annotated[Session, Depends(get_db)]):
    user_obj = service.get_user_by_username(username, db)

    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found: User not found")

    products = get_products(db, username)

    products_shop = ProductShop(
        owner=user_obj,
        products=products
    )
    return success_response(data=products_shop)
