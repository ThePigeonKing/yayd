# syntax=docker/dockerfile:1

FROM python:3.10.7-slim-buster
RUN useradd -m -u 1000 user
WORKDIR /yayd

RUN pip install 'poetry==1.2.0'

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

USER 1000
RUN poetry install
COPY . .

CMD ["poetry", "run", "raise"]

