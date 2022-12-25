# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /SchoolManagement

COPY requirements.txt requirements.txt

RUN apt update && \
    apt -y --no-install-recommends install gcc libc-dev libpq-dev && \
    pip3 install -r requirements.txt

COPY . .

#RUN chmod +x start.sh

EXPOSE 8080

ENV FLASK_APP = src/school_management/run.py
CMD flask run --port=8080
