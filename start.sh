#!/bin/bash

python ./src/create_tables.py

export FLASK_APP=./src/school_management/run.py
flask run --host 0.0.0.0  --port=8080
