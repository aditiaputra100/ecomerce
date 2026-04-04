from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings
from app.shops import models as shop_models  # noqa: F401
from app.payments import models as payment_models  # noqa: F401
from app.categories import models as category_models  # noqa: F401
from app.user.router import auth as auth_router
from app.user.router import user as user_router
from app.products.router import router as product_router
from app.orders.router import router as order_router
from app.shops.router import router as shop_router
from app.payments.router import router as payment_router
from app.categories.router import router as category_router
from . import exceptions
import os

# Create Database Tables
# Note: In production, use Alembic for migrations
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce API (Modular)",
    description="RESTful API for E-Commerce with Modular Architecture",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory if it doesn't exist
os.makedirs("app/static/uploads/products", exist_ok=True)
os.makedirs("app/static/uploads/shops", exist_ok=True)

# Mount Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Add Exception
app.add_exception_handler(exceptions.DuplicateEntryError, exceptions.duplicate_entry_handler)
app.add_exception_handler(exceptions.NotFoundError, exceptions.not_found_handler)
app.add_exception_handler(exceptions.ResourceDisableError, exceptions.resource_disable_handler)

# Include Routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(shop_router)
app.include_router(payment_router)
app.include_router(category_router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to E-Commerce API (Modular Architecture)",
        "docs": "/docs",
        "static_files": "/static"
    }
