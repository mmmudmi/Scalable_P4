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


redis_con = Redis(host="localhost", port=6379)
task_queue = Queue("task_queue", connection=redis_con)
db_session = database.SessionLocal()
