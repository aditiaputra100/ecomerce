from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.products.models import Product


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    icon: Mapped[str | None] = mapped_column(nullable=True)

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")
