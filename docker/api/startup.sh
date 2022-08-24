#!/bin/bash
echo "Dockerizing..."
dockerize -wait tcp://db:5432 -timeout 20s

echo "Run Alembic Migrations and FastAPI with gunicorn"

alembic --raiseerr upgrade head && gunicorn -b 0.0.0.0:8000 -w 4 -k uvicorn.workers.UvicornWorker app.main:app