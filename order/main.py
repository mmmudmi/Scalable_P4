from fastapi import FastAPI
from db import database, models, schemas, crud
from celery import Celery
import os
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

import time

models.Base.metadata.create_all(bind=database.engine)


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
db_session = database.SessionLocal()
celery = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER", "redis://:your-password@localhost:6379/0"),
)

# TRACE
trace_provider = TracerProvider(resource=Resource(attributes={SERVICE_NAME: "order-service"}))
otlp_trace_exporter = OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True)
trace_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

FastAPIInstrumentor.instrument_app(app)


@app.get("/")
async def read_root():
    with tracer.start_as_current_span("parent-span"):
        time.sleep(1)
        with tracer.start_as_current_span("child-span"):
            # root_count.inc(1)
            return {"message": "Hello, world!"}

@app.get("/order")
def get_all_order():
    return crud.get_all(db_session, models.Order)


@app.post("/order")
def create_order(order: schemas.Order):
    with tracer.start_as_current_span("order-span"):
        # orders_count.inc(1)
        if order.id:
            return "Can't create order with specific ID"
        db_order: models.Order = crud.create(db_session, models.Order, order)
        order.id = db_order.id
        celery.send_task("process", args=[order.model_dump()], queue="payment")
        return order


@app.put("/order")
def update_order(order: schemas.Order):
    return crud.update(db_session, models.Order, order)


@app.delete("/order")
def delete_all_order():
    celery.send_task("payment.delete")
    return crud.delete_all(db_session, models.Order)


@app.get("/order/{order_id}")
def get_order(order_id: int):
    return crud.get_by_id(db_session, models.Order, order_id)


@app.delete("/order/{order_id}")
def delete_order(order_id: int):
    return crud.delete(db_session, models.Order, order_id)
