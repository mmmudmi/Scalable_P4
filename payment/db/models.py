from sqlalchemy import Column, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import relationship

from db.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(60), index=True, unique=True, nullable=False)
    credit = Column(Integer, nullable=False)
    payments = relationship("Payment", back_populates="owner")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(60), nullable=False)
    owner = relationship("User", back_populates="payments")
