FROM python:3.9 as base
RUN pip install poetry

WORKDIR /code/
COPY . /code/

RUN poetry install --no-root
