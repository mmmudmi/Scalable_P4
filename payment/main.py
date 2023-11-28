from fastapi import FastAPI
from db import database, models, schemas, crud
from redis import Redis
from rq import Queue
from worker import process
from celery import Celery
import os

models.Base.metadata.create_all(bind=database.engine)


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


celery = Celery("tasks", broker="redis://:your-password@localhost:6379/0")
app = FastAPI()
redis_con = Redis(host="localhost", port=6379)
task_queue = Queue("task_queue", connection=redis_con)
db_session = database.SessionLocal()


@app.get("/payment")
def get_all_payment():
    return crud.get_all(db_session, models.Payment)


@app.post("/payment")
def create_payment(order: schemas.Order):
    if order.id:
        return "Can't create payment with specific ID"
    return process.delay(order.json()).id
    # return crud.create(db_session, models.Payment, schemas.Payment())


@app.put("/payment")
def update_payment(payment: schemas.Order):
    return crud.update(db_session, models.Payment, payment)


@app.delete("/payment")
def delete_all_payment():
    return crud.delete_all(db_session, models.Payment)


@app.get("/payment/{payment_id}")
def get_payment(payment_id: int):
    return crud.get_by_id(db_session, models.Payment, payment_id)


@app.delete("/payment/{payment_id}")
def delete_payment(payment_id: int):
    return crud.delete(db_session, models.Payment, payment_id)
