import glob
import os
import secrets
import shutil

import pytest
from experiments.robo_erectus.utilities import DATABASE_PATH

# from dotenv import load_dotenv
# from sqlalchemy.orm import close_all_sessions

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.dirname(TEST_DIR))

ERECTUS_DIR = os.path.join(ROOT_DIR, "experiments/robo_erectus")


# @pytest.fixture
# def session():
#    from app.database import SessionFactory
#    return SessionFactory()


def pytest_sessionstart(session):
    """runs before all tests start https://stackoverflow.com/a/35394239"""
    print("in sessionstart")
    # temporary change that doesn't persist in the terminal after tests complete:
    # if not load_dotenv(override=True, dotenv_path=os.path.join(baseDir, '.env.test')):
    #    print('failed to load dotenv')
    #    exit(1)
    # assert os.environ['ENV'] == 'test', 'ensure dotenv loaded correctly'


@pytest.fixture(autouse=True)
def run_around_tests():
    """code to run before and afer each test https://stackoverflow.com/a/62784688/5500073"""
    # code that will run before a given test:

    yield
    # code that will run after a given test:
    print("AFTER TEST", flush=True)

    DELETE_GLOBS = [os.path.join(DATABASE_PATH, "unit_test_*")]
    # DELETE_GLOBS = [os.path.join(TEST_DIR, "database/")]
    for pattern in DELETE_GLOBS:
        for dir_name in glob.glob(pattern):
            # print("would delete dir: " + dir_name)
            print("deleting dir: " + dir_name)
            shutil.rmtree(dir_name)

    # close_all_sessions() # prevents pytest from hanging
    # print('finished test cleanup', flush=True)


def get_uuid(length: int = 10):
    return str(secrets.token_hex(length))[:length]
