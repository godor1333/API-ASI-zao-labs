import sys

import pytest
import sqlite3

from auth_manager import AuthManager


# ---------------------------------------------------------------------------
# Фикстуры
# ---------------------------------------------------------------------------
@pytest.fixture
def db():
    """Временная БД SQLite в оперативной памяти."""
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def auth_manager(db):
    """Экземпляр AuthManager, привязанный к тестовой БД."""
    return AuthManager(db)


@pytest.fixture
def users(auth_manager):
    """Три пользователя для параметризованных тестов."""
    auth_manager.register_user("user1", "password123", "CountryA", 1000)
    auth_manager.register_user("user2", "password456", "CountryA", 500)
    auth_manager.register_user("user3", "password789", "CountryB", 250)
    return auth_manager


# ---------------------------------------------------------------------------
# 1. Базовые тесты (3)
# ---------------------------------------------------------------------------
@pytest.mark.basic
def test_register_and_get_user(auth_manager):
    auth_manager.register_user("alice", "secret", "Russia", 1500)
    user = auth_manager.get_user_by_id(1)

    assert user is not None
    assert user[1] == "alice"
    assert user[2] == "secret"
    assert user[3] == "Russia"
    assert user[4] == 1500


@pytest.mark.basic
def test_authenticate_user_success(auth_manager):
    auth_manager.register_user("bob", "qwerty", "Russia", 100)

    user = auth_manager.authenticate_user("bob", "qwerty")

    assert user is not None
    assert user[1] == "bob"


@pytest.mark.basic
def test_delete_user(auth_manager):
    auth_manager.register_user("carol", "pass", "Belarus", 300)
    auth_manager.delete_user(1)

    assert auth_manager.get_user_by_id(1) is None


# ---------------------------------------------------------------------------
# 2. Параметризованные тесты (3)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "country, expected_count",
    [
        ("CountryA", 2),
        ("CountryB", 1),
        ("CountryC", 0),
    ],
)
def test_count_users_by_country(users, country, expected_count):
    assert users.count_users_by_country(country) == expected_count


@pytest.mark.parametrize(
    "username, password, expected_result",
    [
        ("user1", "password123", True),
        ("user1", "wrong-password", False),
        ("unknown", "password123", False),
        ("", "", False),
    ],
)
def test_authenticate_user_parametrized(users, username, password, expected_result):
    user = users.authenticate_user(username, password)
    assert (user is not None) is expected_result


@pytest.mark.parametrize(
    "amount, expected_from, expected_to",
    [
        (100, 900, 600),
        (500, 500, 1000),
        (1000, 0, 1500),
    ],
)
def test_transfer_balance_parametrized(auth_manager, amount, expected_from, expected_to):
    auth_manager.register_user("sender", "p1", "CountryA", 1000)
    auth_manager.register_user("receiver", "p2", "CountryB", 500)

    auth_manager.transfer_balance(1, 2, amount)

    assert auth_manager.get_user_by_id(1)[4] == expected_from
    assert auth_manager.get_user_by_id(2)[4] == expected_to


# ---------------------------------------------------------------------------
# 3. Тестирование исключений (2)
# ---------------------------------------------------------------------------
@pytest.mark.exception
def test_transfer_insufficient_funds_raises(auth_manager):
    auth_manager.register_user("poor", "p1", "CountryA", 100)
    auth_manager.register_user("rich", "p2", "CountryB", 1000)

    with pytest.raises(ValueError, match="Insufficient funds"):
        auth_manager.transfer_balance(1, 2, 500)


@pytest.mark.exception
def test_transfer_from_unknown_user_raises(auth_manager):
    """Документируем дефект: отсутствие пользователя не обработано явно."""
    auth_manager.register_user("receiver", "p2", "CountryB", 1000)

    with pytest.raises(TypeError):
        auth_manager.transfer_balance(999, 1, 100)


# ---------------------------------------------------------------------------
# 4. Тесты безопасности: SQL-инъекции (обязательный тест)
# ---------------------------------------------------------------------------
@pytest.mark.security
def test_sql_injection_authentication_bypass(auth_manager):
    """Инъекция в поле username позволяет войти без корректного пароля.

    Тест проходит => уязвимость подтверждена. Это ожидаемое поведение
    исходного класса AuthManager, который выдаётся в задании.
    """
    auth_manager.register_user("admin", "real-password", "Russia", 1000)

    injected_user = auth_manager.authenticate_user("admin' OR '1'='1", "wrong")

    assert injected_user is not None
    assert injected_user[1] == "admin"


@pytest.mark.security
def test_sql_injection_count_by_country(users):
    """Инъекция в country расширяет выборку на всех пользователей."""
    injected_count = users.count_users_by_country("' OR '1'='1")

    assert injected_count == 3


@pytest.mark.security
@pytest.mark.xfail(
    reason="Ожидаемое безопасное поведение: параметризованный запрос. "
    "На исходном коде падает — это и есть демонстрация уязвимости.",
    strict=True,
)
def test_sql_injection_must_be_blocked(auth_manager):
    auth_manager.register_user("admin", "real-password", "Russia", 1000)

    injected_user = auth_manager.authenticate_user("admin' OR '1'='1", "wrong")

    assert injected_user is None


# ---------------------------------------------------------------------------
# 5. Пропускаемый тест
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Демонстрация пропуска теста: проверка версии Python")
def test_python_version():
    assert sys.version_info >= (3, 7)
