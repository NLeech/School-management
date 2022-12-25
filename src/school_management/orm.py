from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Integer, ForeignKey, Sequence
from flask_restful import fields

Base = declarative_base()


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, Sequence('group_id_seq'), primary_key=True)
    name = Column(String(15), unique=True)
    students = relationship("Student", back_populates="group")

    @classmethod
    def get_fields(cls) -> dict:
        """Return basic Group fields for marshal"""
        return {
            "id": fields.Integer(attribute="id"),
            "name": fields.String(attribute="name")
        }

    @classmethod
    def get_complete_fields(cls) -> dict:
        """Return all Group fields for marshal"""
        data_fields = Group.get_fields()
        data_fields.update({
            "students": fields.List(fields.Nested(Student.get_fields()), attribute="students")
        })
        return data_fields

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"{self.id.__repr__()}, " \
               f"{self.name.__repr__()})"

    def __str__(self):
        return f"id={self.id}, name={self.name}"


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, Sequence('course_id_seq'), primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True)
    description = Column(String(250))

    students = relationship("Student", secondary="assigned_courses", back_populates="courses")

    @classmethod
    def get_fields(cls) -> dict:
        """Return basic Course fields for marshal"""
        return {
            "id": fields.Integer(attribute="id"),
            "name": fields.String(attribute="name"),
            "description": fields.String(attribute="description")
        }

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"{self.id.__repr__()}, " \
               f"{self.name.__repr__()}, " \
               f"{self.description.__repr__()})"

    def __str__(self):
        return f"id={self.id}, name={self.name}, description={self.description}"


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, Sequence('student_id_seq'), primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    first_name = Column(String(150))
    last_name = Column(String(150))

    group = relationship("Group", back_populates="students")
    courses = relationship("Course", secondary="assigned_courses", back_populates="students")

    @classmethod
    def get_fields(cls) -> dict:
        """Return basic Student fields for marshal"""
        return {
            "id": fields.Integer(attribute="id"),
            "first_name": fields.String(attribute="first_name"),
            "last_name": fields.String(attribute="last_name")
        }

    @classmethod
    def get_complete_fields(cls) -> dict:
        """Return all Student fields for marshal"""
        data_fields = Student.get_fields()
        data_fields.update({
            "group": fields.Nested(Group.get_fields(), attribute="group"),
            "courses": fields.List(fields.Nested(Course.get_fields()), attribute="courses")
        })
        return data_fields

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"{self.id.__repr__()}, " \
               f"{self.group_id.__repr__()}, " \
               f"{self.first_name.__repr__()}, " \
               f"{self.last_name.__repr__()})"

    def __str__(self):
        return f"id={self.id}, group_id={self.group_id}, first_name={self.first_name}, last_name={self.last_name}"


class AssignedCourse(Base):
    __tablename__ = "assigned_courses"

    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"{self.student_id.__repr__()}, " \
               f"{self.course_id.__repr__()})"

    def __str__(self):
        return f"student_id={self.student_id}, course_id={self.course_id}"
