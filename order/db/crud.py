from sqlalchemy.orm import Session
from db import schemas, models


def get_all(db: Session, model: models.Base):
    return db.query(model).all()


def delete_all(db: Session, model: models.Base):
    return db.query(model).delete()


def get_by_id(db: Session, model: models.Base, id: int):
    return db.query(model).filter(model.id == id).first()


def create(db: Session, model: models.Base, data: schemas.AbstractBase):
    db_data = model(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


def update(db: Session, model: models.Base, data: schemas.AbstractBase) -> None:
    db.query(model).filter(model.id == data.id).update(data.model_dump())
    db.commit()


def delete(db: Session, model: models.Base, id: int) -> None:
    db.query(model).filter(model.id == id).delete()
    db.commit()
