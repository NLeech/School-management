#!/bin/bash

cd src
python create_tables.py
gunicorn --bind 0.0.0.0:80 -w 1 wsgi:app
