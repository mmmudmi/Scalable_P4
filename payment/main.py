from typing import Any
from celery import Celery
from dotenv import load_dotenv
from db import schemas, database, models
from celery.utils.log import get_task_logger
from kombu import Queue

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
    # TODO rollback process
    pass


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
    print(order_data)
    order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
    user = get_or_create_user(order.user)
    if int(user.credit) < order.total:
        db_session.add(
            models.Payment(id=order.id, user_id=user.id, status="Not enough credit")
        )
        db_session.commit()
        send_rollback(order_data)
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
    order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
    user = (
        db_session.query(models.User).filter(models.User.username == order.user).first()
    )
    user.credit += order.total
    db_session.query(models.User).filter(models.User.id == user.id).update(
        schemas.User.model_validate(user).model_dump()
    )
    db_session.query(models.Payment).filter(models.Payment.id == order.id).update(
        schemas.Payment(id=order.id, user_id=user.id, status=order.error).model_dump()
    )
    db_session.commit()
    send_rollback(order_data)
    return True
