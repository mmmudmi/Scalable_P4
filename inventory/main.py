import os
from typing import Any
from fastapi import FastAPI, Response

from celery import Celery
from celery.utils.log import get_task_logger
from dotenv import load_dotenv
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
# from prometheus_client import Counter, start_http_server, generate_latest
import prometheus_client
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
app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

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

# METRIC
prometheus_client.start_http_server(60)
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="otel-collector:4317", insecure=True))
metric_provider = MeterProvider(resource=Resource(attributes={SERVICE_NAME: "inventory-service"}), metric_readers=[metric_reader])
metrics.set_meter_provider(metric_provider)
meter = metrics.get_meter(__name__)
inventory_count = prometheus_client.Counter(
    "inventory_count",
    "The number of times that inventory is getting deducted"
)
inventory_rollback_count = prometheus_client.Counter(
    "inventory_rollback_count",
    "The number of times that inventory is getting added back"
)
@app.get("/metrics")
def get_metrics():
    return Response(
        media_type="text/plain",
        content=prometheus_client.generate_latest()
    )

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
        inventory_count.inc(1)
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
        inventory_rollback_count.inc(1)
        order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
        item = db_session.query(models.Item).filter(models.Item.name == order.item).first()
        item.quantity += order.amount
        db_session.query(models.Item).filter(models.Item.id == item.id).update(
            schemas.Item.model_validate(item).model_dump()
        )
        db_session.commit()
        send_rollback(order_data)
        return True
