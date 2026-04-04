from typing import TYPE_CHECKING
from sqlalchemy import text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, TimeStampMixin

if TYPE_CHECKING:
    from app.categories.models import Category

class Product(TimeStampMixin, Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[float] = mapped_column(nullable=True)
    stock: Mapped[int] = mapped_column(nullable=True)
    image_url: Mapped[str] = mapped_column(nullable=True)
    slug: Mapped[str] = mapped_column(nullable=True, unique=True)
    is_publish: Mapped[bool] = mapped_column(server_default=text('False'))

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    category_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id', ondelete="SET NULL"), nullable=True)

    owner = relationship('User', back_populates='products')
    category: Mapped['Category | None'] = relationship('Category', back_populates='products')
