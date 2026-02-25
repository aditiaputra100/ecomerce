from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[float] = mapped_column(nullable=True)
    stock: Mapped[int] = mapped_column(nullable=True)
    image_url: Mapped[str] = mapped_column(nullable=True)
    is_publish: Mapped[bool] = mapped_column(server_default=text('False'))

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    owner = relationship('User', back_populates='products')