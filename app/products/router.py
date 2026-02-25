from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Security, status
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated
from app.database import get_db
from app.exceptions import NotFoundError
from app.user.dependencies import get_current_user
from app.user.models import User
from app.schemas import Product
from . import schemas, service

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=List[Product])
def list_products(db: Session = Depends(get_db)):
    return service.get_products(db)

@router.get("/me", response_model=List[schemas.ProductOwner])
def get_my_products(
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db)
):
    return service.get_products_by_user_id(db, current_user.id)

@router.post("/", response_model=Product)
async def create_product(
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    is_publish: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    image_url = None
    if image:
        try:
            image_url = service.save_image(image)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to created product")
    
    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
        "is_publish": is_publish,
        "user_id": current_user.id,
    }

    return service.create_product(db, product_data, image_url)

@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    is_publish: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    # Check ownership
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
    
    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
        "is_publish": is_publish,
    }

    return service.update_product(db, product_id, product_data, image_url)

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=['shopowner'])],
    db: Session = Depends(get_db),
):
    # Check ownership
    product = service.get_product_for_owner(db, product_id, current_user.id)
    
    if not product:
         raw = service.get_product_unchecked(db, product_id)
         if not raw:
            raise NotFoundError(name=f"Product with an ID {product_id} is not found")
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this product")
    
    success = service.delete_product(db, product_id)
    if not success:
         raise HTTPException(status_code=500, detail="Failed to delete product")
    
    return {"detail": "Product deleted"}

@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, db: Annotated[Session, Depends(get_db)]):
    product = service.get_product_by_id(db, product_id)

    if not product:
        raise NotFoundError(name=f"Product with an ID {product_id} is not found")
    
    return product

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

    return {
        "detail": f"Product {'published' if product.is_publish else 'not published'}"
    }