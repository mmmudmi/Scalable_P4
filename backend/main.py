from typing import Annotated, Any

from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db import database, user_services, models, schemas, item_service, order_service
from redis import Redis
from rq import Queue
from jobs.manager import manager
from sqlalchemy.orm import Session
from db.models import Item


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
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    context: dict[str, Any] = {
        "request": request,
    }
    return templates.TemplateResponse("views/home.html", context)


@app.get("/item")
def get_all_item():
    return item_service.get_item_all(database.SessionLocal())


@app.get("/item/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}


@app.post("/item")
def create_item(
    name: Annotated[str, Form()],
    price: Annotated[int, Form()],
    quantity: Annotated[int, Form()],
):
    return item_service.create_item(
        database.SessionLocal(), schemas.Item(name=name, price=price, quantity=quantity)
    )


@app.put("/item/{item_id}")
def read_update_item(
    item_id: int,
    name: Annotated[str, Form()],
    price: Annotated[int, Form()],
    quantity: Annotated[int, Form()],
):
    return {"item_id": item_id}


@app.delete("/item/{item_id}")
def delete_item(item_id: int):
    item_service.deleted_item(database.SessionLocal(), item_id)
    return {"item_id": item_id}


@app.get("/task/{id}")
def payment(id: int):
    jobs = task_queue.enqueue(manager, id)
    return {
        "job_id": jobs.id,
        "waiting_tasks": len(task_queue),
        "current_id": id,
    }


# @app.post("/createItem")
# def create_item():
