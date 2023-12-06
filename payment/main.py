import os
from typing import Any

import requests
from celery import Celery
from dotenv import load_dotenv
from opentelemetry import trace

from db import schemas, database, models

tracer = trace.get_tracer(__name__)

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


def get_or_create_user(username: str):
    user = (
        db_session.query(models.User).filter(models.User.username == username).first()
    )
    if user is not None:
        return user
    new_user = models.User(username=username)
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    return new_user


def send_rollback(order_data: dict[str, Any]):
    requests.put("http://order_service:80/order", json=order_data)


def send_process(order_data: dict[str, Any]):
    celery.send_task("process", args=[order_data], queue="inventory")


@celery.task(name="delete")
def delete():
    db_session.query(models.User).delete()
    db_session.query(models.Payment).delete()
    db_session.commit()
    return True


@celery.task(name="process")
def process(order_data: dict[str, Any]):
    with tracer.start_as_current_span("paymentSpan"):
        print(order_data)
        order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
        user = get_or_create_user(order.user)
        if int(user.credit) < order.total:
            db_session.add(
                models.Payment(id=order.id, user_id=user.id, status="Not enough credit")
            )
            db_session.commit()
            order.status = "Not enough credit"
            send_rollback(order.model_dump())
            return False
        user.credit -= order.total

        db_session.query(models.User).filter(models.User.id == user.id).update(
            schemas.User.model_validate(user).model_dump()
        )
        db_session.add(models.Payment(id=order.id, user_id=user.id))
        db_session.commit()
        send_process(order_data)
        return True


@celery.task(name="rollback")
def rollback(order_data: dict[str, Any]):
    with tracer.start_as_current_span("paymentRollBackSpan"):
        order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
        user = (
            db_session.query(models.User).filter(models.User.username == order.user).first()
        )
        user.credit += order.total
        db_session.query(models.User).filter(models.User.id == user.id).update(
            schemas.User.model_validate(user).model_dump()
        )
        db_session.query(models.Payment).filter(models.Payment.id == order.id).update(
            schemas.Payment(id=order.id, user_id=user.id, status=order.status).model_dump()
        )
        db_session.commit()
        send_rollback(order_data)
        return True
