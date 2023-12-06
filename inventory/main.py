import os
from typing import Any

from celery import Celery
from celery.utils.log import get_task_logger
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor

from db import schemas, database, models
tracer = trace.get_tracer(__name__)

load_dotenv()
celery = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER", "redis://:your-password@localhost:6379/0"),
)
models.Base.metadata.create_all(bind=database.engine)
CeleryInstrumentor().instrument()

logger = get_task_logger(__name__)


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_session = database.SessionLocal()

# TRACE
trace_provider = TracerProvider(resource=Resource(attributes={SERVICE_NAME: "inventory-service"}))
otlp_trace_exporter = OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True)
trace_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

def send_process(order_data: dict[str, Any]):
    celery.send_task("process", args=[order_data], queue="delivery")


def send_rollback(order_data: dict[str, Any]):
    celery.send_task("rollback", args=[order_data], queue="payment")


@celery.task(name="delete")
def delete():
    db_session.query(models.Item).delete()
    db_session.add(models.Item(name="scalable credit", quantity=50))
    db_session.commit()
    return True


@celery.task(name="process")
def process(order_data: dict[str, Any]):
    with tracer.start_as_current_span("inventory-span"):
        order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
        item = db_session.query(models.Item).filter(models.Item.name == order.item).first()
        if item is None:
            order.status = "Invalid Item"
            send_rollback(order.model_dump())
            return "Invalid Item"
        if int(item.quantity) < order.amount:
            order.status = "Out of Stock"
            send_rollback(order.model_dump())
            return "Out of Stock"

        item.quantity -= order.amount
        db_session.query(models.Item).filter(models.Item.id == item.id).update(
            schemas.Item.model_validate(item).model_dump()
        )
        db_session.commit()
        send_process(order_data)
        return True


@celery.task(name="rollback")
def rollback(order_data: dict[str, Any]):
    with tracer.start_as_current_span("inventory-rollback-span"):
        order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
        item = db_session.query(models.Item).filter(models.Item.name == order.item).first()
        item.quantity += order.amount
        db_session.query(models.Item).filter(models.Item.id == item.id).update(
            schemas.Item.model_validate(item).model_dump()
        )
        db_session.commit()
        send_rollback(order_data)
        return True
