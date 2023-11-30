from sqlalchemy import Column, Integer, String

from db.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(60), index=True, nullable=False)
    item = Column(String(60), index=True, nullable=False)
    amount = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    status = Column(String(60), index=True, nullable=False, default="Incomplete")
    error = Column(String(60), nullable=True)
