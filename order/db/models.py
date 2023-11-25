from sqlalchemy import Column, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import relationship

from db.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(60), index=True, nullable=False)
    item = Column(String(60), index=True, nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(String(60), index=True, nullable=False)
