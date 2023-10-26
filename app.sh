#!/bin/sh
sleep 10

alembic upgrade head

sleep 2

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000