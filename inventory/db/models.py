from sqlalchemy import Column, ForeignKey, Integer, String, UUID,Float
from sqlalchemy.orm import relationship

from db.database import Base


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(60), index=True, unique=True, nullable=False)
    quantity = Column(Integer, default=0)
    price = Column(Float,nullable=False) 