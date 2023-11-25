import re
from fastapi import FastAPI
from db import database, models, schemas, crud
from redis import Redis
from rq import Queue


models.Base.metadata.create_all(bind=database.engine)


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
redis_con = Redis(host="localhost", port=6379)
task_queue = Queue("task_queue", connection=redis_con)
db_session = database.SessionLocal()


@app.get("/order")
def get_all_order():
    return crud.get_all(db_session, models.Order)


@app.post("/order")
def create_order(order: schemas.Order):
    return crud.create(db_session, models.Order, order)


@app.get("/order/{order_id}")
def get_order(order_id: int):
    return crud.get_by_id(db_session, models.Order, order_id)
