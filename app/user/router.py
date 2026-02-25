from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from app.database import get_db
from app.schemas import ProductShop
from app.products.service import get_products
from . import schemas, models, service, utils, dependencies

auth = APIRouter(prefix="", tags=["Authentication"])
user = APIRouter(prefix="", tags=["User"])

@auth.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = service.create_user(
        username=user.username,
        email=user.email,
        password=user.password,
        disable=user.disable,
        db=db
    )

    return new_user

@auth.post("/token", response_model=schemas.Token)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = utils.create_access_token(data={"sub": user.username, "scopes": " ".join(form_data.scopes)})
    return {"access_token": access_token, "token_type": "bearer"}

@user.get("/user/me", response_model=schemas.User)
def get_information_user(current_user: Annotated[models.User, Depends(dependencies.get_current_active_user)]):
    return current_user

@user.get("/{username}/products", response_model=ProductShop)
def get_username_catalog(username: str, db: Annotated[Session, Depends(get_db)]):
    user = service.get_user_by_username(username, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found: User not found")


    products = get_products(db, username)

    return ProductShop(
        owner=user,
        products=products
    )

    