from datetime import datetime
from app.database import Base, TimeStampMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column


class FlashSale(TimeStampMixin, Base):
    __tablename__ = "flash_sales"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    items = relationship('FlashSaleItems', back_populates='flash_sale')


class FlashSaleItems(TimeStampMixin, Base):
    __tablename__ = "flash_sale_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    flash_sale_id: Mapped[int] = mapped_column(ForeignKey('flash_sales.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    special_price: Mapped[float] = mapped_column(nullable=False)
    stock_limit: Mapped[int] = mapped_column(nullable=False)
    stock_sold: Mapped[int] = mapped_column(default=0)

    flash_sale = relationship('FlashSale', back_populates='items')
    products = relationship('Product')
