#!/bin/bash

python ./src/create_tables.py

if [ "${FILL_DATABASE}" == "fill" ]; then
  python ./src/fill_database.py
fi

export FLASK_APP=./src/school_management/run.py
flask run --host 0.0.0.0  --port=80
