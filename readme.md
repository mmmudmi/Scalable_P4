docker-compose up

alembic revision --autogenerate

alembic upgrade head

uvicorn main:app --reload

pytest -s

pytest --verbose

pytest
