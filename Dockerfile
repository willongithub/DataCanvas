# syntax=docker/dockerfile:1

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PYTHONUNBUFFERED=TRUE

WORKDIR /app

RUN apt update && \
    apt install -y git build-essential && \
    # apt install -y python3-opencv && \
    apt install -y python3-tk && \
    apt install -y curl
    
RUN python3 -m pip install --upgrade pip setuptools

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false
RUN poetry install

COPY . /app

# ENTRYPOINT [ "poetry", "shell" ]
CMD [ "python", "-m", "datacanvas" ]