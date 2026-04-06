from datetime import datetime
from app.database import Base, TimeStampMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column


class Campaign(TimeStampMixin, Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    items = relationship('CampaignItem', back_populates='campaign')


class CampaignItem(TimeStampMixin, Base):
    __tablename__ = "campaign_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaigns.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    special_price: Mapped[float] = mapped_column(nullable=False)
    stock_limit: Mapped[int] = mapped_column(nullable=False)
    stock_sold: Mapped[int] = mapped_column(default=0)

    campaign = relationship('Campaign', back_populates='items')
    products = relationship('Product')
