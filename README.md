# School management

A small application with REST API for managing students, groups, and courses

Local deployment:
Installing and run:

    git clone https://github.com/NLeech/School-management.git
    cd School-management
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    chmod 755 postgres_init.sh start.sh

Edit file .env to set proper database credentials.
For example, .env file:

    PG_DATABASE="school_management"
    PG_USER="smowner"
    PG_PASSWD="strong_password"
    
    # postgres password
    # PostgreSQL superuser password
    POSTGRES_PASSWORD="pg_strong_password"
    
    # Database address for local deployment
    DATABASE_ADDRESS="127.0.0.1:5432"
    
If the database and database user don't exist, you can create them by running:
    
    export $(grep -v '^#' .env | grep -v '^\s*$' | xargs -d '\n') && sudo -E -u postgres bash ./postgres_init.sh

If it needs, edit postgresql config file pg_hba.conf, refer to [documentation](https://www.postgresql.org/docs/11/auth-pg-hba-conf.html), and restart postgresql server   

Optionally, run script fill_database.py to fill the database with random data

    python3 src/fill_database.py

Run:

    ./start.sh

Then go to [localhost:8082](localhost:8082)

Running tests:  
in virtual environment run:

    coverage run -m unittest tests/unit_test.py -v
    coverage report -m

[GitHub](https://github.com/NLeech/School-management)
