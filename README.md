# School management

A small application with REST API for managing students, groups, and courses

Installing and run:

    git clone 
    cd 
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    chmod 750 src/init_db.sh

Edit config file app.conf to set proper database and database user properties or leave the default settings.
WARNING: for the default settings, existing database named '' will be erased
If it needs, edit postgresql config file pg_hba.conf, refer to [documentation](https://www.postgresql.org/docs/11/auth-pg-hba-conf.html), and restart postgresql server   
Then run:

    src/init_db.sh
    python3 src/create_tables.py

Optionally, run script fill_database.py to fill the database with random data

    python3 src/fill_database.py


Run:

    export FLASK_APP=src/school_management/run.py
    flask run --port=8082

Then go to [localhost:8082](localhost:8082)

Running tests:  
in virtual environment run:

    coverage run -m unittest tests/unit_test.py -v
    coverage report -m

[GitHub]()
