import random
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker, scoped_session, aliased
from .orm import Base, Group, Student, Course
from .generators import generate_groups, generate_students, generate_courses, \
    GROUP_MIN_SIZE, GROUP_MAX_SIZE, MIN_COURSES_PER_STUDENT, MAX_COURSES_PER_STUDENT


class DataAccessLayer:
    def __init__(self, connection_string):
        self.engine = None
        self.Session = None
        self.connection_string = connection_string

    @staticmethod
    def _execute_select_with_pagination(function):
        def wrapper(self, *args, limit: int = 0, offset: int = 0, **kwargs):
            """
            Make select execution with pagination
            :param limit: - quantity of elements in the output
            :param offset: - offset for the output
            :return: query result

            """
            stmt = function(self, *args, **kwargs).offset(offset)
            if limit > 0:
                stmt = stmt.limit(limit)
            return self.Session.execute(stmt).scalars().all()

        return wrapper

    def connect(self) -> None:
        self.engine = create_engine(self.connection_string)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def remove_session(self) -> None:
        self.Session.remove()

    def create_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def assign_students_to_groups(self, a: int = GROUP_MIN_SIZE, b: int = GROUP_MAX_SIZE) -> None:
        """
        Randomly assigns students to groups. Each group could contain from a to b students
        Some groups may be without students or students without groups

        :param a: the minimal quantity of students in a group
        :param b: the maximum quantity of students in a group
        """
        groups = self.Session.execute(select(Group)).scalars()

        for group in groups:
            stmt = select(Student).filter_by(group=None)
            unassigned_students = self.Session.execute(stmt).scalars().all()

            # group could contain from a members
            if len(unassigned_students) < a:
                break

            random_students = random.sample(
                unassigned_students, k=random.randint(
                    a, min(
                        b, len(unassigned_students))))

            for student in random_students:
                student.group = group

            self.Session.add_all(random_students)
            self.Session.flush()

        self.Session.commit()

    def assign_courses_to_students(self, a: int = MIN_COURSES_PER_STUDENT, b: int = MAX_COURSES_PER_STUDENT) -> None:
        """
         Randomly assigns from a to b courses for each student
        (from 1 to 3 by default).
        :param a: the minimal quantity of courses for a student
        :param b: the maximum quantity of courses for a student

        """
        students = self.Session.execute(select(Student)).scalars()
        courses = self.Session.execute(select(Course)).scalars().all()

        for student in students:
            random_courses = random.sample(courses, k=random.randint(a, b))
            student.courses.extend(random_courses)

        self.Session.add_all(students)
        self.Session.commit()

    def fill_database(self) -> dict:
        """
        Fill the database with random test data
        :return: generated test data
        """

        groups = generate_groups()
        students = generate_students()
        courses = generate_courses()

        data = []
        data.extend(list(Group(**item) for item in groups))
        data.extend(list(Student(**item) for item in students))
        data.extend(list(Course(**item) for item in courses))

        self.Session.add_all(data)
        self.Session.commit()

        self.assign_students_to_groups()
        self.assign_courses_to_students()

        return {"groups": groups, "students": students, "courses": courses}

    def get_group_by_name(self, name: str) -> Group:
        """
        Get Group from database by name
        If a Group with the given name doesn't exist, exception NoResultFound will be raised
        :param name: Group name
        :return: Found Group

        """
        return self.Session.execute(select(Group).where(Group.name == name)).one().Group

    def get_course_by_name(self, name: str) -> Course:
        """
        Get Course from database by name
        If a Course with the given name doesn't exist, exception NoResultFound will be raised
        :param name: Course name
        :return: Found Course

        """
        return self.Session.execute(select(Course).where(Course.name == name)).one().Course

    def get_student_by_id(self, student_id: int) -> Student:
        """
        Get Student from database by id
        If a Student with the given id doesn't exist, exception NoResultFound will be raised
        :param student_id: Student id
        :return: Found Student

        """
        return self.Session.execute(select(Student).where(Student.id == student_id)).one().Student

    def add_student(self, student: dict) -> Student:
        """
        Add student to the database
        :param student: dict with student fields {"first_name": first_name, "last_name": last_name}
        :return: Added Student

        """
        new_student = Student(**student)
        self.Session.add(new_student)
        self.Session.commit()
        return new_student

    def delete_student_by_id(self, student_id: int) -> None:
        student = self.get_student_by_id(student_id)
        self.Session.delete(student)
        self.Session.commit()

    def add_student_to_courses(self, student_id: int, courses_list: list) -> Student:
        """
        Add student to the course from list
        :param student_id: Student id
        :param courses_list: list of Course - courses
        :return: Student

        """
        student = self.get_student_by_id(student_id)
        student.courses.extend(courses_list)
        self.Session.add(student)
        self.Session.commit()

        return student

    def delete_student_from_course(self, student_id: int, course: Course) -> Student:
        """
        Delete student from the course
        :param student_id: Student id
        :param course: course
        :return: Student

        """
        student = self.get_student_by_id(student_id)
        student.courses.remove(course)
        self.Session.add(student)
        self.Session.commit()

        return student

    @_execute_select_with_pagination
    def get_students(self, *args, **kwargs) -> list:
        """
        Return list of students
        :return: list of objects

        """
        return select(Student).order_by("id")

    @_execute_select_with_pagination
    def get_groups_with_less_equals_students(self, count: int, *args, **kwargs) -> list:
        """
        Get all groups with fewer or equal students count
        :param count: students count
        :return: groups list

        """
        sub = (
            select([Group, func.count(Group.id).label("group_size")])
            .join(Student.group)
            .group_by(Group.id)
        ).subquery()

        groups = aliased(Group, sub, name="Group")
        stmt = select(groups).where(sub.c.group_size <= count).order_by("id")
        return stmt

    @_execute_select_with_pagination
    def get_students_by_course(self, course_name: str, *args, **kwargs) -> list:
        """
        Get all students related to the course with a given name.
        :param course_name: course name
        :return: students list

        """
        # also check course with course_name exists
        course = self.get_course_by_name(course_name)

        stmt = select(Student).filter(Student.courses.any(Course.name == course.name)).order_by(Student.id)
        return stmt
