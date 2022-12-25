#!/bin/bash

source src/app.conf

sudo -u postgres psql -c "CREATE USER $USER WITH ENCRYPTED PASSWORD '$PASSWD';"
sudo -u postgres psql -c "ALTER USER $USER CREATEDB;"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DATABASE;"
sudo -u postgres psql -c "CREATE DATABASE $DATABASE;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE TO $USER;"
