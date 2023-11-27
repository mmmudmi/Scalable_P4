from db import database, models, schemas, crud
from redis import Redis
from rq import Queue
from db.crud import create
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List


models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


redis_con = Redis(host="localhost", port=6379)
task_queue = Queue("task_queue", connection=redis_con)
db_session = database.SessionLocal()

@app.post("/addItem", response_model=schemas.Item)
def create_item(item: schemas.Item, db: Session = Depends(get_db)):
    return crud.create(db=db, model=models.Item, data=item)

@app.get("/items", response_model=List[schemas.Item])
def create_item(db: Session = Depends(get_db)):
    return crud.get_all(db=db, model=models.Item)

@app.get("/item/{id}", response_model=schemas.Item)
def get_item(id:int,db: Session = Depends(get_db)):
    return crud.get_by_id(db=db, model=models.Item,id=id)

@app.delete("/deleteItem/{id}")
def delete_item(id: int,db: Session = Depends(get_db)):
    return crud.delete(db=db, model=models.Item, id=id)

@app.delete("/deleteItems")
def create_item(db: Session = Depends(get_db)):
    return crud.delete_all(db=db, model=models.Item)

@app.put("/updateItem")
def update_item(item: schemas.Item, db: Session = Depends(get_db)):
    return crud.update(db=db, model=models.Item, data=item)

