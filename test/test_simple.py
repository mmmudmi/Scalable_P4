import requests
from typing import Final
import pytest

BASE_URL: Final[str] = "http://localhost:80/order"


class TestSimple:
    def test_complete(self):
        json_data: dict = {
            "user": "user001",
            "amount": 10,
            "item": "scalable credit",
            "total": 50,
        }
        requests.post(BASE_URL, json=json_data)

    def test_same_user(self):
        json_data: dict = {
            "user": "user001",
            "amount": 10,
            "item": "scalable credit",
            "total": 50,
        }
        requests.post(BASE_URL, json=json_data)

    def test_out_of_credit(self):
        json_data: dict = {
            "user": "user001",
            "amount": 10,
            "item": "scalable credit",
            "total": 50,
        }
        requests.post(BASE_URL, json=json_data)

    def test_invalid_item(self):
        json_data: dict = {
            "user": "user002",
            "amount": 10,
            "item": "funpar credit",
            "total": 50,
        }
        requests.post(BASE_URL, json=json_data)

    def test_out_of_stock(self):
        json_data: dict = {
            "user": "user003",
            "amount": 100,
            "item": "scalable credit",
            "total": 10,
        }
        requests.post(BASE_URL, json=json_data)

    def test_delivery(self):
        json_data: dict = {
            "user": "user004",
            "amount": 10,
            "item": "scalable credit",
            "total": 50,
            "error": "delivery",
        }
        requests.post(BASE_URL, json=json_data)
