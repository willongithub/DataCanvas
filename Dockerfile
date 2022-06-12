# syntax=docker/dockerfile:1

FROM python:3.9-slim

WORKDIR /usr/src/app

COPY . .

CMD [ "python", "-m", "datacanvas"]