from flask import request, jsonify, make_response, current_app
from flask_restful import Resource, marshal, abort
from sqlalchemy.exc import NoResultFound
from .orm import Group, Student


def get_data_with_pagination(data_fields: dict, getter, *args, **kwargs) -> list | dict:
    """
    Get data from the database with pagination
    :param data_fields:  dict of fields for a response marshalling
    :param getter: function - data getter
    :return: data

    """
    data = marshal(getter(
        *args,
        limit=request.args.get("limit", default=50, type=int),
        offset=request.args.get("offset", default=0, type=int),
        **kwargs
    ),
        data_fields)

    return data


def send_error_response(code: int, message: str) -> None:
    """
    Create end send custom error
    :param code:  HTTP status code
    :param message: response message

    """
    response = make_response(jsonify(message=message), code)
    abort(response)


class Students(Resource):
    def get(self):
        data = get_data_with_pagination(Student.get_complete_fields(), current_app.database.get_students)
        return {"data": data, "root_name": "students"}

    def post(self):
        # If parsing is unsuccessful, there is no error thrown . Instead "Bad Request" is returned to the client.
        new_student = request.get_json()

        if not isinstance(new_student, dict) \
                or new_student.get("first_name", None) is None \
                or new_student.get("last_name", None) is None:
            send_error_response(400, f"Invalid data fields: '{new_student}'.")

        data = marshal(current_app.database.add_student(new_student), Student.get_complete_fields())
        return {"data": data, "root_name": "student"}


class StudentsDelete(Resource):
    def delete(self, student_id: int):
        try:
            current_app.database.delete_student_by_id(student_id)
        except NoResultFound:
            send_error_response(404, f"Student with ID '{student_id}' does not exist.")

        return {"data": {"success": True}, "root_name": "result"}


class StudentsByCourse(Resource):
    def get(self, course_name):
        try:
            data = get_data_with_pagination(
                Student.get_complete_fields(),
                current_app.database.get_students_by_course,
                course_name)
        except NoResultFound:
            send_error_response(404, f"Course named '{course_name}' not found")
        return {"data": data, "root_name": "students"}


class StudentsAddToCourses(Resource):
    def put(self, student_id):
        courses = request.args.getlist("courses")
        if len(courses) == 0:
            send_error_response(404, f"Courses not listed")

        try:
            courses_list = []
            for course_name in courses:
                courses_list.append(current_app.database.get_course_by_name(course_name))
        except NoResultFound:
            send_error_response(404, f"Course named '{course_name}' not found")

        try:
            data = marshal(current_app.database.add_student_to_courses(student_id, courses_list),
                           Student.get_complete_fields())
        except NoResultFound:
            send_error_response(404, f"Student with ID '{student_id}' does not exist.")
        return {"data": data, "root_name": "student"}


class StudentsDeleteFromCourse(Resource):
    def put(self, student_id):
        course_name = request.args.get("course_name", default=None)
        if course_name is None:
            send_error_response(404, f"Course not specified")

        try:
            course = current_app.database.get_course_by_name(course_name)
        except NoResultFound:
            send_error_response(404, f"Course named '{course_name}' not found")

        try:
            data = marshal(current_app.database.delete_student_from_course(student_id, course),
                           Student.get_complete_fields())
        except ValueError:
            send_error_response(404, f"Student with ID '{student_id}' not assigned to course '{course_name}'.")
        except NoResultFound:
            send_error_response(404, f"Student with ID '{student_id}' does not exist.")
        return {"data": data, "root_name": "student"}


class GroupsByCount(Resource):
    def get(self, count):
        data = get_data_with_pagination(
            Group.get_complete_fields(),
            current_app.database.get_groups_with_less_equals_students,
            count
        )
        return {"data": data, "root_name": "groups"}


class GroupsByGroup(GroupsByCount):
    def get(self, group_name):
        try:
            # also check group with group_name exists
            group = current_app.database.get_group_by_name(group_name)
        except NoResultFound:
            send_error_response(404, f"Group '{group_name}' does not exist.")
        return super().get(len(group.students))
