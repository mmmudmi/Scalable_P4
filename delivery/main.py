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
import prometheus_client
import logging
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry._logs import set_logger_provider
from db import schemas, database, models

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
trace_provider = TracerProvider(resource=Resource(attributes={SERVICE_NAME: "delivery-service"}))
otlp_trace_exporter = OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True)
trace_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

# METRIC
prometheus_client.start_http_server(50)
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="otel-collector:4317", insecure=True))
metric_provider = MeterProvider(resource=Resource(attributes={SERVICE_NAME: "delivery-service"}), metric_readers=[metric_reader])
metrics.set_meter_provider(metric_provider)
meter = metrics.get_meter(__name__)
delivery_count = prometheus_client.Counter(
    "delivery_count",
    "The number of deliveries being made"
)
delivery_rollback_count = prometheus_client.Counter(
    "delivery_rollback_count",
    "The number of deliveries getting rolled back"
)

# LOGGING
logger_provider = LoggerProvider(resource=Resource(attributes={SERVICE_NAME: "delivery-service"}))
otlp_log_exporter = OTLPLogExporter(endpoint="otel-collector:4317", insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))
handler = LoggingHandler(level=logging.DEBUG, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def send_rollback(order_data: dict[str, Any]):
    celery.send_task("rollback", args=[order_data], queue="inventory")

def send_process(order_data: dict[str, Any]):
    requests.put("http://order_service:80/order", json=order_data)

@app.get("/metrics")
def get_metrics():
    return Response(
        media_type="text/plain",
        content=prometheus_client.generate_latest()
    )

@celery.task(name="delete")
def delete():
    db_session.query(models.Delivery).delete()
    db_session.commit()
    return True


@celery.task(name="process")
def process(order_data: dict[str, Any]):
    with tracer.start_as_current_span("delivery-span"):
        delivery_count.inc(1)
        order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
        if order.error is not None and "delivery" in order.error:
            logger.error("Can't deliver")
            order.status = "Can't delivery"
            db_session.add(
                models.Delivery(id=order.id, username=order.user, status=order.error)
            )
            db_session.commit()
            send_rollback(order.model_dump())
            return False
        logger.info("Delivery processing...")
        db_session.add(
            models.Delivery(id=order.id, username=order.user, status="Completed")
        )
        db_session.commit()
        order.status = "Delivered"
        send_process(order.model_dump())
        return True


# @celery.task(name="rollback")
# def rollback(order_data: dict[str, Any]):
#     with tracer.start_as_current_span("delivery-rollback-span"):
#         delivery_rollback_count.inc(1)
#         order: schemas.Order = schemas.Order.model_validate(order_data, strict=True)
#         user = (
#             db_session.query(models.User).filter(models.User.username == order.user).first()
#         )
#         user.credit += order.total
#         db_session.query(models.User).filter(models.User.id == user.id).update(
#             schemas.User.model_validate(user).model_dump()
#         )
#         db_session.add(models.Payment(id=order.id, user_id=user.id, status=order.error))
#         db_session.commit()
#         send_rollback(order_data)
#         return True
