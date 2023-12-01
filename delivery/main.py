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


def send_rollback(order_data: dict[str, Any]):
    celery.send_task("inventory_rollback", args=[order_data])


def send_process(order_data: dict[str, Any]):
    # TODO update order
    pass


@celery.task(name="delivery_delete")
def delete():
    db_session.query(models.Delivery).delete()
    db_session.commit()
    return True


@celery.task(name="delivery_process")
def process(order_data: dict[str, Any]):
    order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
    if "delivery" in order.error:
        db_session.add(
            models.Delivery(id=order.id, username=order.user, status=order.error)
        )
        db_session.commit()
        send_rollback(order_data)
        return False
    db_session.add(
        models.Delivery(id=order.id, username=order.user, status="Completed")
    )
    db_session.commit()
    send_process(order_data)
    return True


# @celery.task(name="delivery_rollback")
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
