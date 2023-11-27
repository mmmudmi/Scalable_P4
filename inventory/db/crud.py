from sqlalchemy.orm import Session
from db import schemas, models


def get_all(db: Session, model: models.Base):
    return db.query(model).all()


def delete_all(db: Session, model: models.Base):
    db.query(model).delete()
    db.commit()
    return {"detail": "All items deleted"}


def get_by_id(db: Session, model: models.Base, id: int):
    return db.query(model).filter(model.id == id).first()


def create(db: Session, model: models.Base, data: schemas.AbstractBase):
    db_data = model(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


def update(db: Session, model: models.Base, data: schemas.AbstractBase):
    item = db.query(model).filter(model.id == data.id).first()
    if item:
        db.query(model).filter(model.id == data.id).update(data.model_dump())
        db.commit()
        return {"detail": f"Updated id: {data.id} successfully"}
    else:
        return {"detail": f"Item with id: {data.id} not found"}
    


def delete(db: Session, model: models.Base, id: int):
    item = db.query(model).filter(model.id == id).first()
    if item:
        db.delete(item)
        db.commit()
        return {"detail": f"Deleted id: {id} successfully"}
    else:
        return {"detail": f"Item with id: {id} not found"}
    

