#!/bin/bash

echo "Run Alembic Migrations"
echo "Create initial data in DB and Run FastAPI with gunicorn"
alembic --raiseerr upgrade head &&\

# python -m app.initial_data && \
gunicorn -b 0.0.0.0:80 -w 4 -k uvicorn.workers.UvicornWorker app.main:app