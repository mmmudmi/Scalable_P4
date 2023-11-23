from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(60), index=True)
    credit = Column(Integer, default=100)

    orders = relationship("Order", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(60), index=True)
    price = Column(Integer)
    quantity = Column(Integer)

    orders = relationship("Order", back_populates="item")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    quantity = Column(Integer)
    process = Column(Integer)
    status = Column(String(20))

    owner = relationship("User", back_populates="orders")
    item = relationship("Items", back_populates="orders")
