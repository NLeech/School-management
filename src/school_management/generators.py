import random
import string

GROUPS_QTY = 10
STUDENTS_QTY = 200

GROUP_MIN_SIZE = 10
GROUP_MAX_SIZE = 30

MIN_COURSES_PER_STUDENT = 1
MAX_COURSES_PER_STUDENT = 3

student_first_names = [
    "James",
    "John",
    "Robert",
    "Michael",
    "William",
    "David",
    "Richard",
    "Joseph",
    "Charles",
    "Thomas",
    "Mary",
    "Patricia",
    "Jennifer",
    "Elizabeth",
    "Linda",
    "Barbara",
    "Susan",
    "Margaret",
    "Jessica",
    "Sarah"
]
student_last_names = [
    "Smith",
    "Murphy",
    "Jones",
    "Williams",
    "O'Kelly",
    "Brown",
    "Walsh",
    "Taylor",
    "Davies",
    "O'Brien",
    "Miller",
    "Wilson",
    "Garcia",
    "Rodriguez",
    "O'Neill",
    "Li",
    "Lam",
    "Lee",
    "White",
    "Anderson"
]
courses = [
    ("English", "English"),
    ("World Literature", "World Literature"),
    ("Art", "Art"),
    ("Physics", "Physics"),
    ("Chemistry", "Chemistry"),
    ("Biology", "Biology"),
    ("Geology", "Geology"),
    ("Astronomy", "Astronomy"),
    ("Algebra", "Algebra"),
    ("Geometry", "Geometry")
]


def generate_random_group() -> str:
    """Generate a random string like LL_DD"""
    prefix = "".join(random.choices(string.ascii_uppercase, k=2))
    number = "".join(random.choices(string.digits, k=2))
    return f"{prefix}_{number}"


def generate_random_tuple(list1: list, list2: list) -> tuple:
    """
    Generate tuple with random item from lists
    :param list1: first list
    :param list2: second list
    :return: two random values from both lists

    """
    return random.choice(list1), random.choice(list2)


def generate_random_list(generator, *args, k: int = 0) -> list:
    """
    Generate list with unique items from generator function
    :param generator: function - item generator
    :param k: list size
    :return: list with unique items

    """
    result = []
    while len(result) < k:
        item = generator(*args)
        if not(item in result):
            result.append(item)

    return result


def generate_students(
        first_names: list = None,
        last_names: list = None,
        qty: int = STUDENTS_QTY) -> list:
    """
    Generate qty students with unique random names
    :param first_names: list with available first names
    :param last_names: list with available second names
    :param qty: generated students quantity
    :return: list of dict like {"first_name": first_name, "last_name", last_name}

    """
    if first_names is None:
        first_names = student_first_names
    if last_names is None:
        last_names = student_last_names

    names_list = generate_random_list(
        generate_random_tuple, first_names, last_names, k=qty)
    return list({"first_name": item[0], "last_name": item[1]}
                for item in names_list)


def generate_groups(qty: int = GROUPS_QTY) -> list:
    """
    Generate qty groups with unique random names like LL_DD
    :param qty: generated groups quantity
    :return: list of dict like {"name": group_name}

    """
    group_list = generate_random_list(generate_random_group, k=qty)
    return list({"name": item} for item in group_list)


def generate_courses(courses_list: list = None) -> list:
    """Convert courses list to list of dict like {"mane": course_name, "description": group_description}"""
    if courses_list is None:
        courses_list = courses

    return list({"name": item[0], "description": item[1]}
                for item in courses_list)
