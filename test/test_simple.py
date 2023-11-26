from requests import request
from typing import Final
import pytest

BASE_URL: Final[str] = "localhost:800"


@pytest.fixture
def setup_database():
    print("Setup database")
    yield
    print("Teardown database")


@pytest.fixture
def setup_config():
    print("Setup configuration")
    yield
    print("Teardown configuration")


class TestSimple:
    def setup_method(self, method):
        print("Setup before each test method")

    def teardown_method(self, method):
        print("Teardown after each test method")

    def test_addition(self, setup_database, setup_config):
        assert 1 + 1 == 2

    def test_subtraction(self, setup_database, setup_config):
        assert 3 - 1 == 2
