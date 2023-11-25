from sqlalchemy import Column, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import relationship

from db.database import Base


class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(60), index=True, nullable=False)
    status = Column(String(60), index=True, nullable=False)
