#!/bin/bash
echo "Add User Group"
# useradd -s /bin/bash -m ${USER_NAME} &&
# export HOME=/home/${USER_NAME} &&
# usermod -u ${USER_ID} ${USER_NAME} &&
# groupadd -g ${GROUP_ID} ${GROUP_NAME} && 
# usermod -g ${GROUP_NAME} ${USER_NAME} &&


echo "Dockerizing..."
dockerize -wait tcp://db:5432 -timeout 20s

echo "Run Alembic Migrations and FastAPI with gunicorn"
alembic --raiseerr upgrade head && \
gunicorn -b 0.0.0.0:8000 -w 4 -k uvicorn.workers.UvicornWorker app.main:app