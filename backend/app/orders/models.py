from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from app.database import Base
from app.products.models import Product
from app.user.models import User

if TYPE_CHECKING:
    from app.payments.models import Payment

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total_price: Mapped[float] = mapped_column()
    status: Mapped[str] = mapped_column(default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")
    payment: Mapped["Payment | None"] = relationship("Payment", back_populates="order", uselist=False)

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column()
    price: Mapped[float] = mapped_column()

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()
