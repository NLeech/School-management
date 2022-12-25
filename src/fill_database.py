from school_management import create_database_connection


if __name__ == "__main__":
    db = create_database_connection()
    db.fill_database()
