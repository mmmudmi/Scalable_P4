from sqlalchemy.orm import Session
from db import schemas, models


def get_order_all(db: Session) -> schemas.Order:
    return db.query(models.Order).all()


def get_order(db: Session, order_id: int) -> schemas.Order | None:
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def create_order(db: Session, order: schemas.Order):
    db_order = models.Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order_credit(db: Session, order: schemas.Order) -> None:
    db.query(models.Order).filter(models.Order.id == order.id).update(
        order.model_dump()
    )
    db.commit()


def deleted_order(db: Session, order_id: int) -> None:
    db.query(models.Order).filter(models.Order.id == order_id).delete()
    db.commit()
