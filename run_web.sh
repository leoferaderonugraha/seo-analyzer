#!/bin/sh

export FLASK_DEBUG=true
export FLASK_APP=src/py/app.py
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=1405

poetry install --no-root &&
poetry run flask run