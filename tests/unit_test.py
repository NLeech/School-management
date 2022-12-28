import unittest
from xml.etree import ElementTree
from flask_restful import marshal, fields
from sqlalchemy import create_engine, select, func
from sqlalchemy.exc import NoResultFound
from parameterized import parameterized
from school_management import Group, Course, Student, app, create_database_connection, API_VERSION
from school_management.generators import GROUPS_QTY, STUDENTS_QTY, \
    GROUP_MIN_SIZE, GROUP_MAX_SIZE, \
    MIN_COURSES_PER_STUDENT, MAX_COURSES_PER_STUDENT

TEST_DATABASE = "school_management_test_123"

test_database_connection_string = (f"postgresql://{app.config['USER']}:"
                                   f"{app.config['PASSWD']}@"
                                   f"{app.config['DATABASE_ADDRESS']}/"
                                   f"{TEST_DATABASE}")

postgres_connection_string = (f"postgresql://{app.config['USER']}:"
                              f"{app.config['PASSWD']}@"
                              f"{app.config['DATABASE_ADDRESS']}/"
                              "postgres")

test_data = {}


def setUpModule():
    unittest.TestLoader.sortTestMethodsUsing = None

    engine = create_engine(postgres_connection_string)
    connection = engine.connect()

    # close transaction, postgres does not allow to create or drop databases
    # inside transactions
    connection.execute("COMMIT")

    connection.execute(f"DROP DATABASE IF EXISTS {TEST_DATABASE}")
    connection.execute("COMMIT")
    connection.execute(f"CREATE DATABASE {TEST_DATABASE}")
    connection.close()

    db = create_database_connection(test_database_connection_string)
    db.create_tables()

    global test_data
    test_data = db.fill_database()

    db.remove_session()

    db.engine.dispose()


def tearDownModule():
    engine = create_engine(postgres_connection_string)
    connection = engine.connect()

    # close all connections
    connection.execute(f"""SELECT pg_terminate_backend(pg_stat_activity.pid)
                            FROM pg_stat_activity
                            WHERE pg_stat_activity.datname = '{TEST_DATABASE}';
                            """)
    connection.execute("COMMIT")
    connection.execute(f"DROP DATABASE IF EXISTS {TEST_DATABASE}")
    connection.close()


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.db = create_database_connection(test_database_connection_string)
        app.config["DATABASE"] = TEST_DATABASE
        self.app = app.test_client()

    def tearDown(self):
        self.db.remove_session()


class TestTestData(BaseTest):

    def test_groups_quantity(self):
        self.assertTrue(len(test_data["groups"]) == GROUPS_QTY)

    def test_students_quantity(self):
        self.assertTrue(len(test_data["students"]) == STUDENTS_QTY)

    @parameterized.expand([
        ("groups", Group, {"name": fields.String}),
        ("courses", Course, {"name": fields.String,
                             "description": fields.String}),
        ("students", Student, {
            "first_name": fields.String, "last_name": fields.String})
    ])
    def test_data(self, name, orm_object, serializer):
        db_data = marshal(self.db.Session.execute(select(orm_object)).scalars().all(), serializer)
        self.assertCountEqual(test_data[name], list(dict(i) for i in db_data))

    def test_groups_assigning(self):
        min_groups_with_students = STUDENTS_QTY // GROUP_MAX_SIZE + 1
        stmt = (
            select(func.count(Group.id))
            .join(Student.group)
            .group_by(Group.id)
        )
        result = self.db.Session.execute(stmt).scalars().all()

        # there are exist at least min_groups_with_students groups with students
        self.assertTrue(len(result) >= min_groups_with_students)
        self.assertTrue(min(result) >= GROUP_MIN_SIZE)
        self.assertTrue(max(result) <= GROUP_MAX_SIZE)

    def test_courses_assigning(self):
        # there are no students without courses
        stmt = select(func.count(Course.name)).join(Student.courses).group_by(Student)
        result = self.db.Session.execute(stmt).scalars().all()
        self.assertTrue(len(result) == STUDENTS_QTY)

        # max and min courses per student
        self.assertTrue(min(result) >= MIN_COURSES_PER_STUDENT)
        self.assertTrue(max(result) <= MAX_COURSES_PER_STUDENT)

    def test_unassigned_students(self):
        # there are exist maximum students without group
        stmt = select(Student).filter_by(group=None)
        unassigned_students = self.db.Session.execute(stmt).scalars().all()
        max_unassigned_students = STUDENTS_QTY - GROUPS_QTY * GROUP_MIN_SIZE
        self.assertTrue(len(unassigned_students) <= max_unassigned_students)


class TestPagination(BaseTest):
    def test_pagination(self):
        res = self.app.get(f"/api/v{API_VERSION}/students/?limit=20&offset=5")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json["students"]), 20)
        self.assertEqual(res.json["students"][0]["id"], 6)


class TestXMLOutput(BaseTest):
    def test_xml_output(self):
        self.app.environ_base["HTTP_ACCEPT"] = "application/xml"
        res = self.app.get(f"/api/v{API_VERSION}/students/?limit=20&offset=5")
        self.assertEqual(res.status_code, 200)
        root = ElementTree.fromstring(res.text)
        elements = list(item for item in root)
        self.assertEqual(len(elements), 20)
        self.assertEqual(elements[0][0].text, "6")
        self.assertEqual(elements[0][0].tag, "id")


class TestGroupsByCount(BaseTest):
    def setUp(self):
        super().setUp()

        self.test_groups = [Group(name="test group 1"), Group(name="test group 2")]
        self.db.Session.add_all(self.test_groups)
        self.db.Session.flush()

        self.test_students = [
            Student(first_name="test student1", last_name="test student 1", group=self.test_groups[0]),
            Student(first_name="test student2", last_name="test student 2", group=self.test_groups[1]),
            Student(first_name="test student3", last_name="test student 3", group=self.test_groups[1])
        ]
        self.db.Session.add_all(self.test_students)
        self.db.Session.commit()

    def tearDown(self):
        for item in self.test_students:
            self.db.Session.delete(item)
        for item in self.test_groups:
            self.db.Session.delete(item)

        self.db.Session.commit()
        super().tearDown()

    @parameterized.expand([
        ("int count json", f"/api/v{API_VERSION}/groups_by_count/2/"),
        ("count from group json", f"/api/v{API_VERSION}/groups_by_group/test group 2/",)
    ])
    def test_groups_by_count(self, name, route):
        res = self.app.get(route)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json["groups"]), 2)
        self.assertEqual(res.json["groups"][0]["name"], "test group 1")
        self.assertEqual(res.json["groups"][1]["name"], "test group 2")

    def test_group_not_found(self):
        res = self.app.get(f"/api/v{API_VERSION}/groups_by_group/non-existing group/")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json["message"], "Group 'non-existing group' does not exist.")


class TestAddStudent(BaseTest):

    def test_add_student(self):
        res = self.app.post(f"/api/v{API_VERSION}/students/",
                            data='{"first_name": "Chuck","last_name": "Norris"}',
                            content_type="application/json")
        self.assertEqual(res.status_code, 200)

        # check output
        self.assertEqual(res.get_json()["student"]["first_name"], "Chuck")

        # check in database
        student = self.db.Session.execute(select(Student).where(Student.first_name == "Chuck")).one().Student
        self.assertEqual(student.last_name, "Norris")

        self.db.Session.delete(student)
        self.db.Session.commit()

    def test_add_student_wrong_data(self):
        res = self.app.post(f"/api/v{API_VERSION}/students/",
                            data='{"wrong_field": "Chuck","last_name": "Norris"}',
                            content_type="application/json")
        self.assertEqual(res.status_code, 400)


class TestDeleteStudent(BaseTest):
    def test_delete_student_by_id(self):
        student = Student(first_name="test student1", last_name="test student 1")
        self.db.Session.add(student)
        self.db.Session.commit()

        res = self.app.delete(f"/api/v{API_VERSION}/students/{student.id}")
        self.assertEqual(res.status_code, 200)

        # check in db
        with self.assertRaises(NoResultFound):
            self.db.Session.execute(select(Student).where(Student.id == student.id)).one()

    def test_delete_student_by_id_wrong_id(self):
        res = self.app.delete(f"/api/v{API_VERSION}/students/{STUDENTS_QTY + 50}")
        self.assertEqual(res.status_code, 404)

    def test_delete_student_by_id_wrong_id_type(self):
        res = self.app.delete(f"/api/v{API_VERSION}/students/wrong_id")
        self.assertEqual(res.status_code, 405)


class TestGetStudentsByCourse(BaseTest):
    def test_get_students_by_course(self):
        # get the first course for the first student
        course = self.db.Session.execute(select(Student).where(Student.id == 1)).one().Student.courses[0]

        res = self.app.get(f"/api/v{API_VERSION}/students_by_course/{course.name}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.get_json()["students"]), len(course.students))

    def test_get_students_by_course_wrong_course(self):
        res = self.app.get(f"/api/v{API_VERSION}/students_by_course/wrong_course/")
        self.assertEqual(res.status_code, 404)
        self.assertIn("Course named", res.text)


class TestAddStudentToCourses(BaseTest):
    def setUp(self):
        super().setUp()

        self.test_courses = [Course(name="test course 1"), Course(name="test course 2")]
        self.db.Session.add_all(self.test_courses)
        self.db.Session.flush()

        self.test_students = [
            Student(first_name="test student1", last_name="test student 1"),
        ]
        self.db.Session.add_all(self.test_students)
        self.db.Session.commit()

    def tearDown(self):
        for item in self.test_students:
            self.db.Session.delete(item)

        for item in self.test_courses:
            self.db.Session.delete(item)

        self.db.Session.commit()
        super().tearDown()

    def test_add_student_to_courses(self):
        student = self.db.Session.execute(select(Student).where(Student.first_name == "test student1")).one().Student

        res = self.app.put(f"/api/v{API_VERSION}/students_add_to_courses/{student.id}/"
                           f"?courses=test course 1&courses=test course 2")
        self.assertEqual(res.status_code, 200)

        # check output
        self.assertEqual(res.get_json()["student"]["first_name"], "test student1")
        self.assertEqual(len(res.get_json()["student"]["courses"]), 2)
        self.assertEqual(res.get_json()["student"]["courses"][1]["name"], "test course 2")

        # check in db
        self.db.Session.refresh(student)
        self.assertEqual(len(student.courses), 2)

    @parameterized.expand([
        ("wrong_id",
         f"/api/v{API_VERSION}/students_add_to_courses/{STUDENTS_QTY + 1}/?courses=test course 1&courses=test course 2",
         "Student with ID"),
        ("wrong_course", f"/api/v{API_VERSION}/students_add_to_courses/1/?courses=test course 1&courses=wrong course",
         "Course named")
    ])
    def test_add_test_add_student_to_courses_exceptions(self, name, route, responce):
        res = self.app.put(route)
        self.assertEqual(res.status_code, 404)
        self.assertIn(responce, res.text)


class TestDeleteStudentFromCourse(BaseTest):
    def setUp(self):
        super().setUp()

        self.test_course = Course(name="test course 1")
        self.db.Session.add(self.test_course)
        self.db.Session.flush()

        self.test_student = Student(
            first_name="test student1",
            last_name="test student 1",
            courses=[self.test_course]
        )
        self.db.Session.add(self.test_student)
        self.db.Session.commit()

    def tearDown(self):
        self.db.Session.delete(self.test_student)
        self.db.Session.delete(self.test_course)
        self.db.Session.commit()
        super().tearDown()

    def test_del_student_from_course(self):
        res = self.app.put(f"/api/v{API_VERSION}/students_del_from_course/{self.test_student.id}/"
                           f"?course_name=test course 1")
        self.assertEqual(res.status_code, 200)

        # check output
        self.assertEqual(res.get_json()["student"]["first_name"], "test student1")
        self.assertEqual(len(res.get_json()["student"]["courses"]), 0)

        # check in db
        self.db.Session.refresh(self.test_student)
        self.assertEqual(len(self.test_student.courses), 0)

    def test_del_student_from_course_wrong_id(self):
        res = self.app.put(f"/api/v{API_VERSION}/students_del_from_course/{STUDENTS_QTY + 1}/"
                           f"?course_name=test course 1")
        self.assertEqual(res.status_code, 404)
        self.assertIn("Student with ID", res.text)

    @parameterized.expand([
        ("wrong_course_name", "?course_name=wrong course", "Course named"),
        ("wrong_course", "?course_name=Art", "not assigned to course"),
        ("no_course", "", "Course not specified")
    ])
    def test_del_student_from_course_exceptions(self, name, parameter, response):
        res = self.app.put(f"/api/v{API_VERSION}/students_del_from_course/{self.test_student.id}/{parameter}")
        self.assertEqual(res.status_code, 404)
        self.assertIn(response, res.text)


if __name__ == "__main__":
    unittest.main()
