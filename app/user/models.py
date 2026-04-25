from typing import TYPE_CHECKING
from sqlalchemy import text
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.database import Base

if TYPE_CHECKING:
    from app.shops.models import Shop

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    disable: Mapped[bool] = mapped_column(default=False, server_default=text('False'))

    products: Mapped[list['Product']] = relationship('Product', back_populates='owner')
    orders: Mapped[list['Order']] = relationship("Order", back_populates="owner")
    shop: Mapped['Shop | None'] = relationship("Shop", back_populates="owner", uselist=False)
