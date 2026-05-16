from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from app.database import get_db
from app.config import settings
from app.schemas import ProductShop, SuccessResponse, ProductsOnShop
from app.products.service import get_products
from . import schemas, models, service, dependencies

auth = APIRouter(prefix="", tags=["Authentication"])
user = APIRouter(prefix="", tags=["User"])


def _set_refresh_cookie(response: Response, refresh_token: str, max_age: int) -> None:
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
        samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
        max_age=max_age,
        path=settings.REFRESH_TOKEN_COOKIE_PATH,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        path=settings.REFRESH_TOKEN_COOKIE_PATH,
    )

@auth.post("/register", status_code=status.HTTP_201_CREATED, response_model=SuccessResponse[schemas.AuthSession, None])
def register(user_data: schemas.UserCreate, response: Response, db: Session = Depends(get_db)):
    new_user = service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        disable=user_data.disable,
        db=db
    )
    session = service.issue_session(new_user, db)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    _set_refresh_cookie(response, session.refresh_token, int(refresh_token_expires.total_seconds()))
    
    return SuccessResponse(
        message="User created successfully",
        data=schemas.AuthSession(
            access_token=session.access_token,
            token_type="bearer",
            user=schemas.User.model_validate(session.user),
        ),
    )

@auth.post("/token", response_model=SuccessResponse[schemas.AuthSession, None])
def token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user_obj = service.authenticate_user(form_data.username, form_data.password, db)
    session = service.issue_session(user_obj, db)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    _set_refresh_cookie(response, session.refresh_token, int(refresh_token_expires.total_seconds()))

    return SuccessResponse(
        message="",
        data=schemas.AuthSession(
            access_token=session.access_token,
            token_type="bearer",
            user=schemas.User.model_validate(session.user),
        ),
    )


@auth.post("/token/refresh", response_model=SuccessResponse[schemas.AuthSession, None])
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token_value = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)

    if not refresh_token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    session = service.rotate_session(refresh_token_value, db)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    _set_refresh_cookie(response, session.refresh_token, int(refresh_token_expires.total_seconds()))

    return SuccessResponse(
        message="",
        data=schemas.AuthSession(
            access_token=session.access_token,
            token_type="bearer",
            user=schemas.User.model_validate(session.user),
        ),
    )


@auth.post("/logout", response_model=SuccessResponse[None, None])
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token_value = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)

    if refresh_token_value:
        service.revoke_session(refresh_token_value, db)

    _clear_refresh_cookie(response)

    return SuccessResponse(message="Logged out successfully", data=None)

@user.get("/user/me", response_model=SuccessResponse[schemas.User, None])
def get_information_user(current_user: Annotated[models.User, Depends(dependencies.get_current_active_user)]):
    return SuccessResponse(message="", data=schemas.User.model_validate(current_user))

@user.get("/{username}/products", response_model=SuccessResponse[ProductShop, None])
def get_username_catalog(username: str, db: Annotated[Session, Depends(get_db)]):
    user_obj = service.get_user_by_username(username, db)

    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found: User not found")

    products = get_products(db, username)

    products_owner = [ProductsOnShop.model_validate(product) for product in products]

    products_shop = ProductShop(
        owner=schemas.User.model_validate(user_obj),
        products=products_owner
    )
    return SuccessResponse(message="", data=products_shop)
