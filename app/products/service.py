import os
import uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.exceptions import ResourceDisableError
from app.user.models import User
from . import models, schemas

UPLOAD_DIR = "app/static/uploads/products"

def save_image(file: UploadFile) -> str:
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    return f"/static/uploads/products/{unique_filename}"

def get_products(db: Session, username: str | None = None):
    query = db.query(models.Product).filter(models.Product.is_publish == True)
    if username:
        query = query.join(models.Product.owner).filter(User.username == username)
    return query.all()

def get_products_by_user_id(db: Session, user_id: int):
    return db.query(models.Product).filter(models.Product.user_id == user_id).all()

def create_product(db: Session, product_data: dict, image_url: str = None):
    db_product = models.Product(**product_data, image_url=image_url)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product_unchecked(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_product_by_id(db: Session, product_id: int):
    product = get_product_unchecked(db, product_id)
    
    if product and not product.is_publish:
        raise ResourceDisableError(name=f"{product.name} is not publish")

    return product

def get_product_for_owner(db: Session, product_id: int, user_id: int):
    product = get_product_unchecked(db, product_id)
    if product and product.user_id == user_id:
        return product
    return None

def update_product(db: Session, product_id: int, product_data: dict, image_url: str = None):
    # This assumes ownership check is done by caller or we trust caller if checking purely by ID here?
    # Better to fetch raw and update. But caller should usually provide the product or check ownership.
    # Let's keep it simple: fetch raw, update. Ownership validation is Router's job via `get_product_for_owner` or similar.
    # Wait, previous implementation in my thought used `get_product_by_id` which had checks.
    # Let's use `get_product_unchecked` here so we can update unpublished ones.
    db_product = get_product_unchecked(db, product_id)
    if not db_product:
        return None
    
    for key, value in product_data.items():
        setattr(db_product, key, value)
    
    if image_url:
        # Delete old image if exists? (Optional improvement)
        if db_product.image_url:
            old_path = f"app{db_product.image_url}"
            if os.path.exists(old_path):
                os.remove(old_path)
        db_product.image_url = image_url

    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    # Use raw to allow deleting unpublished
    db_product = get_product_unchecked(db, product_id)
    if db_product:
        # Hapus file gambar jika ada
        if db_product.image_url:
            file_path = f"app{db_product.image_url}"
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.delete(db_product)
        db.commit()
        return True
    return False
