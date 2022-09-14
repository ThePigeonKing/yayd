# syntax=docker/dockerfile:1

FROM python:3.10.7-slim-buster

WORKDIR /yayd
COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

RUN pip install 'poetry==1.2.0'
RUN poetry install
COPY . .
CMD ["poetry", "run", "raise"]

