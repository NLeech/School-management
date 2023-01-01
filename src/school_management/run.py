import os
import json

from flask import Flask, make_response, current_app
from flask_restful import Api
from flasgger import Swagger

from .db import DataAccessLayer
from .api import (
    Students,
    GroupsByCount,
    GroupsByGroup,
    StudentsByCourse,
    StudentsDelete,
    StudentsAddToCourses,
    StudentsDeleteFromCourse
)
from .dict_to_xml import dict_to_xml

API_VERSION = 1

app = Flask(__name__)
app.config.from_pyfile(os.path.join(".", "../../.env"))

api = Api(app, default_mediatype="application/json")


def get_connection_string() -> str:
    if 'IS_DOCKER' in os.environ:
        connection_string = (f"postgresql://{os.environ.get('PG_USER')}:"
                             f"{os.environ.get('PG_PASSWD')}@"
                             f"{os.environ.get('PG_DATABASE_ADDRESS')}/"
                             f"{os.environ.get('PG_DATABASE')}")

    else:
        connection_string = (f"postgresql://{app.config['PG_USER']}:"
                             f"{app.config['PG_PASSWD']}@"
                             f"{app.config['DATABASE_ADDRESS']}/"
                             f"{app.config['PG_DATABASE']}")
    return connection_string


@app.before_first_request
def init_db():
    current_app.database = create_database_connection(get_connection_string())


@api.representation('application/json')
def json_response(data, code, headers):
    resp = make_response(json.dumps({data["root_name"]: data["data"]}, indent="\t"), code)
    resp.headers.extend(headers)
    return resp


@api.representation('application/xml')
def xml_response(data, code, headers):
    resp = make_response(dict_to_xml(data["data"], data["root_name"]), code)
    resp.headers.extend(headers)
    return resp


@app.teardown_request
def shutdown_session(exception=None):
    current_app.database.Session.remove()


def create_database_connection(connection_string: str = None) -> DataAccessLayer:
    """Create DataAccessLayer and make database connection"""
    if connection_string is None:
        connection_string = get_connection_string()

    db = DataAccessLayer(connection_string)
    db.connect()
    return db


api.add_resource(Students, f"/api/v{API_VERSION}/students/")
api.add_resource(StudentsDelete, f"/api/v{API_VERSION}/students/<int:student_id>")
api.add_resource(StudentsByCourse, f"/api/v{API_VERSION}/students_by_course/<string:course_name>/")
api.add_resource(StudentsAddToCourses, f"/api/v{API_VERSION}/students_add_to_courses/<int:student_id>/")
api.add_resource(StudentsDeleteFromCourse, f"/api/v{API_VERSION}/students_del_from_course/<int:student_id>/")

api.add_resource(GroupsByCount, f"/api/v{API_VERSION}/groups_by_count/<int:count>/")
api.add_resource(GroupsByGroup, f"/api/v{API_VERSION}/groups_by_group/<string:group_name>/")

app.config['SWAGGER'] = {"openapi": "3.0.3"}

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'specifications',
            "route": '/specifications.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/",
    "specs_route": "/"
}

swagger = Swagger(app, template_file="apidocs.yaml", config=swagger_config)

if __name__ == "__main__":
    app.run()
