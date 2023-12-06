import os
from typing import Any
from fastapi import FastAPI, Response

import requests
from celery import Celery
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
trace_provider = TracerProvider(resource=Resource(attributes={SERVICE_NAME: "payment-service"}))
otlp_trace_exporter = OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True)
trace_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

# METRIC
prometheus_client.start_http_server(70)
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="otel-collector:4317", insecure=True))
metric_provider = MeterProvider(resource=Resource(attributes={SERVICE_NAME: "payment-service"}), metric_readers=[metric_reader])
metrics.set_meter_provider(metric_provider)
meter = metrics.get_meter(__name__)
payment_count = prometheus_client.Counter(
    "payment_count",
    "The number of payments being made"
)
payment_rollback_count = prometheus_client.Counter(
    "payment_rollback_count",
    "The number of payments getting rolled back"
)
@app.get("/metrics")
def get_metrics():
    return Response(
        media_type="text/plain",
        content=prometheus_client.generate_latest()
    )

def get_or_create_user(username: str):
    user = (
        db_session.query(models.User).filter(models.User.username == username).first()
    )
    if user is not None:
        return user
    new_user = models.User(username=username)
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    return new_user


def send_rollback(order_data: dict[str, Any]):
    requests.put("http://order_service:80/order", json=order_data)


def send_process(order_data: dict[str, Any]):
    celery.send_task("process", args=[order_data], queue="inventory")


@celery.task(name="delete")
def delete():
    db_session.query(models.User).delete()
    db_session.query(models.Payment).delete()
    db_session.commit()
    return True


@celery.task(name="process")
def process(order_data: dict[str, Any]):
    with tracer.start_as_current_span("payment-span"):
        # payment_count.add(1)
        payment_count.inc(1)
        print(order_data)
        order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
        user = get_or_create_user(order.user)
        if int(user.credit) < order.total:
            db_session.add(
                models.Payment(id=order.id, user_id=user.id, status="Not enough credit")
            )
            db_session.commit()
            order.status = "Not enough credit"
            send_rollback(order.model_dump())
            return False
        user.credit -= order.total

        db_session.query(models.User).filter(models.User.id == user.id).update(
            schemas.User.model_validate(user).model_dump()
        )
        db_session.add(models.Payment(id=order.id, user_id=user.id))
        db_session.commit()
        send_process(order_data)
        return True


@celery.task(name="rollback")
def rollback(order_data: dict[str, Any]):
    with tracer.start_as_current_span("payment-rollback-span"):
        payment_rollback_count.inc(1)
        order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
        user = (
            db_session.query(models.User).filter(models.User.username == order.user).first()
        )
        user.credit += order.total
        db_session.query(models.User).filter(models.User.id == user.id).update(
            schemas.User.model_validate(user).model_dump()
        )
        db_session.query(models.Payment).filter(models.Payment.id == order.id).update(
            schemas.Payment(id=order.id, user_id=user.id, status=order.status).model_dump()
        )
        db_session.commit()
        send_rollback(order_data)
        return True
