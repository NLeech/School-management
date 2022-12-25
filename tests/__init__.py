# console test 'coverage run -m unittest tests/unit_test.py -v'
# did not work without it
import os
import sys
PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(PROJECT_PATH, "src")
sys.path.append(SOURCE_PATH)
