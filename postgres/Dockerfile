# syntax=docker/dockerfile:1

FROM postgres:15

COPY healthchecks healthchecks

COPY postgres_init.sh /docker-entrypoint-initdb.d/postgres_init.sh
