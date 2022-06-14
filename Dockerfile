# syntax=docker/dockerfile:1

FROM python:3.8-slim

WORKDIR /app

COPY pyproject.toml /app

RUN python3 -m pip install --upgrade pip setuptools
RUN python3 -m pip install poetry
RUN apt update
RUN apt install -y python3-tk
# RUN curl -sSL https://install.python-poetry.org | python3 -
# ENV PATH="$HOME/.local/bin:${PATH}"
# RUN poetry config virtualenvs.create false
RUN poetry install

COPY . .

CMD [ "poetry", "run", "python", "-m", "datacanvas"]