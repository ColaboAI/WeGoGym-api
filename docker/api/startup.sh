#!/bin/bash
echo "Dockerizing..."
dockerize -wait tcp://db:5432 -timeout 20s

echo "Run Alembic Migrations and FastAPI with gunicorn"

alembic upgrade head && gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app