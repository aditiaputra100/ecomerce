import os
import uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.exceptions import ResourceDisableError, FileMaximumError
from app.user.models import User
from app.categories.service import get_category
from . import models, schemas

UPLOAD_DIR = "app/static/uploads/products"

def save_image(file: UploadFile) -> str:
    max_size_5_mb = 5 * 1024 * 1024

    if file.size > max_size_5_mb:
        raise FileMaximumError("Maximum file is 5MB")

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    file_extension:str = os.path.splitext(file.filename)[1]

    if file_extension.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Invalid file type")

    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    return f"/static/uploads/products/{unique_filename}"

def delete_image(image_url: str) -> bool:
    if not image_url:
        return False

    file_path = f"app{image_url}"

    if os.path.exists(file_path):
        os.remove(file_path)
        return True

    return False

def get_products(db: Session, username: str | None = None):
    query = db.query(models.Product).filter(models.Product.is_publish == True)
    if username:
        query = query.join(models.Product.owner).filter(User.username == username)
    return query.all()

def get_best_seller_products(db: Session):
    pass

def get_recommended_products(db: Session):
    pass

def get_discount_products(db: Session):
    pass

def get_products_by_user_id(db: Session, user_id: int):
    return db.query(models.Product).filter(models.Product.user_id == user_id).all()

def create_product(db: Session, product_data: dict):
    name: str = product_data.get('name', '')
    name = name.strip()

    description: str = product_data.get('description', '')
    description = description.strip()

    price: float = product_data.get('price', 0)
    stock: int = product_data.get('stock', 0)
    is_publish: bool = product_data.get('is_publish', False)
    category_id: int | None = product_data.get('category_id', None)
    image: UploadFile = product_data.get('image', None)

    if name == "":
        raise ValueError("Name cannot be empty")
    
    if price <= 0:
        raise ValueError("Price cannot be lower than equal 0")
    
    if stock < 0:
        raise ValueError("Stock cannot be lower than 0")
    
    category = get_category(db=db, category_id=category_id)

    if not category:
        raise ValueError('Category is not found')
    
    if not image:
        raise ValueError('Image is required')

    try: 
        image_url = save_image(image)

    except OSError as err:
        raise RuntimeError(err.strerror)

    db_product = models.Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        is_publish=is_publish,
        user_id=product_data.get('user_id'),
        category_id=category_id,
        image_url=image_url,
    )

    try:
        db.add(db_product)
        db.flush()

        product_slug = f'{name.lower().replace(" ", "-")}-{db_product.id}'
        db_product.slug = product_slug

        db.commit()
    except Exception as err:
        db.rollback()
        delete_image(image_url)
        raise RuntimeError(f"Database error: {str(err)}")

    return db_product

def get_product_unchecked(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_product_by_id(db: Session, product_id: int):
    product = get_product_unchecked(db, product_id)
    
    if product and not product.is_publish:
        raise ResourceDisableError(name=f"{product.name} is not publish")

    return product

def get_product_by_slug(db: Session, slug: str):
    product = db.query(models.Product).filter(models.Product.slug == slug).first()
    
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
        delete_image(db_product.image_url)
        db_product.image_url = image_url

    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    # Use raw to allow deleting unpublished
    db_product = get_product_unchecked(db, product_id)
    if db_product:
        delete_image(db_product.image_url)
        
        db.delete(db_product)
        db.commit()
        return True
    return False
