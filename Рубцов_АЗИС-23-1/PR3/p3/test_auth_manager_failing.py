"""Заведомо падающий тест: демонстрация красного прогона pytest.

Ожидаемое значение указано НЕВЕРНО специально, чтобы увидеть,
как pytest показывает ошибку assert с диффом.
"""
import sqlite3

import pytest

from auth_manager import AuthManager


@pytest.fixture
def db():
    """Соединение с SQLite в памяти; закрывается после теста."""
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def auth_manager(db):
    """Экземпляр AuthManager на in-memory базе."""
    return AuthManager(db)


def test_transfer_balance_wrong_expectation(auth_manager, db):
    """После перевода 200 от user1 (1000) к user2 (500) ожидаем 900 у user1 —
    это НЕВЕРНО (правильно 800), тест должен упасть."""
    auth_manager.register_user("user1", "password123", "CountryA", 1000)
    auth_manager.register_user("user2", "password123", "CountryB", 500)

    auth_manager.transfer_balance(1, 2, 200)

    cursor = db.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = 1")
    balance1 = cursor.fetchone()[0]

    assert balance1 == 900  # намеренная ошибка: реальный баланс 800
