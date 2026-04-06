from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    Security,
    status,
)
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated
from app.database import get_db
from app.exceptions import NotFoundError, FileMaximumError
from app.user.dependencies import get_current_user
from app.user.models import User
from app.schemas import success_response, Product
from app.categories.models import Category
from . import schemas, service

router = APIRouter(prefix="/products", tags=["Products"])


def _ensure_shop_owner(current_user: User) -> bool:
    if not current_user.shop:
        return False
    
    return True


def _validate_category(db: Session, category_id: Optional[int]):
    if category_id is None:
        return None
    category = db.query(Category).filter(Category.id == category_id, Category.is_active == True).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found or inactive")
    return category

@router.get("/")
def list_products(category: Optional[str] = None, username: str | None = None, db: Session = Depends(get_db)):
    products = service.get_products(db, username=username)
    return success_response(data=products, message="Products retrieved successfully")

@router.get("/homepage", response_model=schemas.ProductHomePage)
async def products_homepage():
    pass

@router.get("/me")
def get_my_products(
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db)
):
    _ensure_shop_owner(current_user)
    products = service.get_products_by_user_id(db, current_user.id)
    return success_response(data=products, message="Your products retrieved successfully")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    is_publish: bool = Form(False),
    category_id: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    if not _ensure_shop_owner(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must open a shop before managing products",
        )

    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
        "is_publish": is_publish,
        "user_id": current_user.id,
        "category_id": category_id,
        "image": image,
    }

    try:
        response_data = service.create_product(db, product_data)

    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err)
        )
    
    except FileMaximumError as err:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=str(err)
        )
    
    except RuntimeError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err)
        )
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occured"
        )
    
    product = Product.model_validate(response_data)
    return success_response(data=product, message="Product created successfully", status_code=201)

@router.put("/{product_id}")
async def update_product(
    product_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    is_publish: bool = Form(False),
    category_id: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    _ensure_shop_owner(current_user)
    product = service.get_product_for_owner(db, product_id, current_user.id)
    if not product:
        # Check if product exists at all to give correct error (404 vs 403)
        # But for security, maybe just 404 is better to hide existence?
        # Or 403 if it exists but not owned.
        # Let's try to fetch raw to distinguish.
        raw = service.get_product_unchecked(db, product_id)
        if not raw:
            raise NotFoundError(name=f"Product with an ID {product_id} is not found")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this product")

    image_url = None
    if image:
        try:
            image_url = service.save_image(image)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to upload image")
    
    _validate_category(db, category_id)

    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
        "is_publish": is_publish,
        "category_id": category_id,
    }

    updated_product = service.update_product(db, product_id, product_data, image_url)
    return success_response(data=updated_product, message="Product updated successfully")

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=['shopowner'])],
    db: Session = Depends(get_db),
):
    # Check ownership
    _ensure_shop_owner(current_user)
    product = service.get_product_for_owner(db, product_id, current_user.id)
    
    if not product:
         raw = service.get_product_unchecked(db, product_id)
         if not raw:
            raise NotFoundError(name=f"Product with an ID {product_id} is not found")
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this product")
    
    success = service.delete_product(db, product_id)
    if not success:
         raise HTTPException(status_code=500, detail="Failed to delete product")
    
    return success_response(data=None, message="Product deleted successfully")

@router.get("/{product_id}")
def get_product(product_id: int, db: Annotated[Session, Depends(get_db)]):
    product = service.get_product_by_id(db, product_id)

    if not product:
        raise NotFoundError(name=f"Product with an ID {product_id} is not found")
    
    return success_response(data=product, message="Product retrieved successfully")

@router.patch("/{product_id}/publish")
def publish_product(
    product_id: int, 
    current_user: Annotated[User, Security(get_current_user, scopes=['shopowner'])],
    db: Session = Depends(get_db),
):
    product = service.get_product_unchecked(db, product_id)

    if not product:
        raise NotFoundError(name=f"Product with an ID {product_id} is not found")
    
    if product.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this product")
    
    product.is_publish = not product.is_publish

    db.commit()

    message = f"Product {'published' if product.is_publish else 'not published'}"
    return success_response(data=product, message=message)
