docker-compose up

alembic revision --autogenerate

alembic upgrade head

uvicorn main:app --reload

celery -A worker.celery worker -E --pool=solo --loglevel=info

pytest -s

pytest --verbose

pytest
