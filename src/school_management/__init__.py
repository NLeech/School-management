"""
Simple school management application
provides students list, groups list, courses list
include postgres database support

"""
from .run import app, create_database_connection, API_VERSION
from .db import DataAccessLayer
from .orm import Group, Student, Course
