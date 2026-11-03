"""Демонстрационные падающие тесты для скриншота «неправильный результат».

Запуск:
    python -m pytest test_failure_demo.py -v --maxfail=2 --tb=short

Тесты намеренно содержат неверные ожидаемые значения.
"""

import sqlite3

import pytest

from auth_manager import AuthManager


@pytest.fixture
def manager():
    connection = sqlite3.connect(":memory:")
    yield AuthManager(connection)
    connection.close()


def test_wrong_expected_balance_after_transfer(manager):
    manager.register_user("sender", "p1", "CountryA", 1000)
    manager.register_user("receiver", "p2", "CountryB", 500)

    manager.transfer_balance(1, 2, 200)

    # Ошибка в ожидании: фактический баланс 800, а не 900
    assert manager.get_user_by_id(1)[4] == 900


def test_wrong_expected_user_count(manager):
    manager.register_user("u1", "p", "CountryA", 100)
    manager.register_user("u2", "p", "CountryA", 100)

    # Ошибка в ожидании: фактическое количество 2, а не 3
    assert manager.count_users_by_country("CountryA") == 3


def test_this_failure_is_not_reached(manager):
    # Благодаря --maxfail=2 pytest остановится раньше этого теста
    assert False
