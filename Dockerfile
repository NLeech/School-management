# build stage
FROM python:3.10-slim as builder

WORKDIR /School-management

ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && \
    apt-get -y --no-install-recommends install curl gcc libc-dev libpq-dev

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /School-management/wheels -r requirements.txt


# final stage
FROM python:3.10-slim

WORKDIR /School-management

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl

COPY --from=builder /School-management/wheels /wheels
COPY --from=builder /School-management/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY . .

RUN chmod +x start.sh

EXPOSE 80

CMD ./start.sh

