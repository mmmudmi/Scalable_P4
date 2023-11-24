from sqlalchemy.orm import Session
from db import schemas, models


def get_item_all(db: Session) -> schemas.Item:
    return db.query(models.Item).all()


def get_item(db: Session, item_id: int) -> schemas.Item | None:
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def create_item(db: Session, item: schemas.Item):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item_credit(db: Session, item: schemas.Item) -> None:
    db.query(models.Item).filter(models.Item.id == item.id).update(item.model_dump())
    db.commit()


def deleted_item(db: Session, item_id: int) -> None:
    db.query(models.Item).filter(models.Item.id == item_id).delete()
    db.commit()
