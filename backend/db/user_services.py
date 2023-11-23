from sqlalchemy.orm import Session
from db import schemas, models


def get_user_all(db: Session) -> schemas.User:
    return db.query(models.User).all()


def create_user(db: Session, user: schemas.User):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_credit(db: Session, user_id: int, credit: int) -> None:
    db.query(models.User).filter(models.User.id == user_id).update({"credit": credit})
    db.commit()


def deleted_user(db: Session, user_id: int) -> None:
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
