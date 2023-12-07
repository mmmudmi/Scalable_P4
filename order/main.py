from fastapi import FastAPI, Response
from db import database, models, schemas, crud
from celery import Celery
import os
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
import time
import logging
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter


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
CeleryInstrumentor().instrument()

# TRACE
trace_provider = TracerProvider(resource=Resource(attributes={SERVICE_NAME: "order-service"}))
otlp_trace_exporter = OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True)
trace_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

# METRIC
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="otel-collector:4317", insecure=True))
metric_provider = MeterProvider(resource=Resource(attributes={SERVICE_NAME: "order-service"}), metric_readers=[metric_reader])
metrics.set_meter_provider(metric_provider)
meter = metrics.get_meter(__name__)
order_count = prometheus_client.Counter(
    "order_count",
    "The number of orders being made"
)

# LOGGING
logger_provider = LoggerProvider(resource=Resource(attributes={SERVICE_NAME: "order-service"}))
otlp_log_exporter = OTLPLogExporter(endpoint="otel-collector:4317", insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))
handler = LoggingHandler(level=logging.DEBUG, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logger = logging.getLogger(__name__)


FastAPIInstrumentor.instrument_app(app)

@app.get("/metrics")
def get_metrics():
    return Response(
        media_type="text/plain",
        content=prometheus_client.generate_latest()
    )


@app.get("/")
async def read_root():
    with tracer.start_as_current_span("parent-span"):
        time.sleep(1)
        logger.info("HELLO WORLD!",extra={"user":"mimi"})
        with tracer.start_as_current_span("child-span"):
            # root_count.inc(1)
            return {"message": "Hello, world!"}

@app.get("/order")
def get_all_order():
    return crud.get_all(db_session, models.Order)


@app.post("/order")
def create_order(order: schemas.Order):
    with tracer.start_as_current_span("order-span"):
        logger.info("Order being made", extra={"user":order.user,"item":order.item,"amount":order.amount,"total":order.total})
        order_count.inc(1)
        if order.id:
            logger.error("Can't create order with specific ID",extra={"user":order.user})
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
