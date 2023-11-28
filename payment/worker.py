import os
from celery import Celery, Task
from dotenv import load_dotenv
from db import schemas, database, models, crud

load_dotenv()
celery = Celery("tasks", broker="redis://:your-password@localhost:6379/0")
models.Base.metadata.create_all(bind=database.engine)


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_session = database.SessionLocal()


@celery.task(name="process", bind=True)
def process(self: Task, data: schemas.Order):
    print(self.request.id)
    print("HELLO")
    # crud.create(db_session, models.Payment, data)
    return True


# @celery.task(name="rollback", bind=True)
# def rollback(data):
#     print(self.request.id)
#     pass
