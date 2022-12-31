# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /SchoolManagement

COPY requirements.txt requirements.txt

RUN apt-get update && \
    apt-get -y --no-install-recommends install curl gcc libc-dev libpq-dev && \
    pip3 install -r requirements.txt

COPY . .

RUN chmod +x start.sh

EXPOSE 8080

CMD ./start.sh
