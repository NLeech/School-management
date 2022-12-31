#!/bin/bash

python ./src/create_tables.py

export FLASK_APP=./src/school_management/run.py
flask run --port=8080
