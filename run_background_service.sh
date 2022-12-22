#!/bin/sh

poetry install --no-root &&
poetry run python src/py/background_service.py