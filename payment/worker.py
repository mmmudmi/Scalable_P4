import os
from celery import Celery, Task
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


@celery.task(name="process", bind=True)
def process(self, data: schemas.Order):
    # logger.info(f"HELLO {self.request.id}")
    # crud.create(db_session, models.Payment, data)
    crud.create(
        db_session,
        models.User,
        schemas.User(id=1, username=self.request.id, credit=100),
    )
    return True


# @celery.task(name="rollback", bind=True)
# def rollback(data):
#     print(self.request.id)
#     pass
