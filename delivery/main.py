import os
from typing import Any

import requests
from celery import Celery
from dotenv import load_dotenv

from db import schemas, database, models

load_dotenv()
celery = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER", "redis://:your-password@localhost:6379/0"),
)
models.Base.metadata.create_all(bind=database.engine)


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_session = database.SessionLocal()


def send_rollback(order_data: dict[str, Any]):
    celery.send_task("rollback", args=[order_data], queue="inventory")


def send_process(order_data: dict[str, Any]):
    requests.put("http://order_service:80/order", json=order_data)


@celery.task(name="delete")
def delete():
    db_session.query(models.Delivery).delete()
    db_session.commit()
    return True


@celery.task(name="process")
def process(order_data: dict[str, Any]):
    order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
    if order.error is not None and "delivery" in order.error:
        order.status = "Can't delivery"
        db_session.add(
            models.Delivery(id=order.id, username=order.user, status=order.status)
        )
        db_session.commit()
        send_rollback(order.model_dump())
        return False
    db_session.add(
        models.Delivery(id=order.id, username=order.user, status="Completed")
    )
    db_session.commit()
    order.status = "Completed"
    send_process(order.model_dump())
    return True


# @celery.task(name="rollback")
# def rollback(order_data: dict[str, Any]):
#     order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
#     user = (
#         db_session.query(models.User).filter(models.User.username == order.user).first()
#     )
#     user.credit += order.total
#     db_session.query(models.User).filter(models.User.id == user.id).update(
#         schemas.User.model_validate(user).model_dump()
#     )
#     db_session.add(models.Payment(id=order.id, user_id=user.id, status=order.error))
#     db_session.commit()
#     send_rollback(order_data)
#     return True
