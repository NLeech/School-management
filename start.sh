#!/bin/bash

cd src

python create_tables.py

if [ "${FILL_DATABASE}" == "fill" ]; then
  python fill_database.py
fi

gunicorn --bind 0.0.0.0:80 -w 1 wsgi:app
