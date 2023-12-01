from typing import Any
from celery import Celery
from dotenv import load_dotenv
from db import schemas, database, models, crud
from celery.utils.log import get_task_logger

load_dotenv()
celery = Celery("tasks", broker="redis://:your-password@localhost:6379/0")
models.Base.metadata.create_all(bind=database.engine)
logger = get_task_logger(__name__)


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_session = database.SessionLocal()


def send_process(order_data: dict[str, Any]):
    celery.send_task("delivery_process", args=[order_data])


def send_rollback(order_data: dict[str, Any]):
    celery.send_task("payment_rollback", args=[order_data])
    pass


@celery.task(name="inventory_delete")
def delete():
    db_session.query(models.Item).delete()
    db_session.commit()
    return True


@celery.task(name="inventory_process")
def process(order_data: dict[str, Any]):
    order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
    item = db_session.query(models.Item).filter(models.Item.name == order.item).first()
    if item is None:
        order.error = "Invalid Item"
        send_rollback(order.model_dump())
        return False
    if int(item.quantity) < order.amount:
        order.error = "Out of Stock"
        send_rollback(order.model_dump())
        return False

    item.quantity -= order.amount
    db_session.query(models.Item).filter(models.Item.id == item.id).update(
        schemas.Item.model_validate(item).model_dump()
    )
    db_session.commit()
    send_process(order_data)
    return True


@celery.task(name="inventory_rollback")
def rollback(order_data: dict[str, Any]):
    order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
    item = db_session.query(models.Item).filter(models.Item.name == order.item).first()
    item.quantity += order.amount
    db_session.query(models.Item).filter(models.Item.id == item.id).update(
        schemas.Item.model_validate(item).model_dump()
    )
    db_session.commit()
    send_rollback(order_data)
    return True
