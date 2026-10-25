"""Практика 3. Тесты класса AuthManager с использованием pytest.

Демонстрируются: фикстуры, метки (маркеры), параметризация,
проверка исключений, пропуск тестов и тесты на SQL-инъекции.
"""
import sqlite3
import sys

import pytest

from auth_manager import AuthManager


# ---------------------------------------------------------------------------
# Фикстуры
# ---------------------------------------------------------------------------

@pytest.fixture
def db():
    """Соединение с SQLite в памяти; закрывается после каждого теста."""
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def auth_manager(db):
    """Экземпляр AuthManager, работающий с in-memory базой."""
    return AuthManager(db)


def get_balance(db, user_id):
    """Вспомогательная функция: читает баланс пользователя напрямую из БД."""
    cursor = db.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()[0]


# ---------------------------------------------------------------------------
# Базовые тесты
# ---------------------------------------------------------------------------

@pytest.mark.basic
def test_register_and_get_user_by_id(auth_manager):
    """Регистрация пользователя и получение его по id: поля сохранены верно."""
    auth_manager.register_user("alice", "pass123", "Uzbekistan", 1000)

    user = auth_manager.get_user_by_id(1)

    # Строка: (id, username, password, country, balance)
    assert user is not None
    assert user[0] == 1
    assert user[1] == "alice"
    assert user[2] == "pass123"
    assert user[3] == "Uzbekistan"
    assert user[4] == 1000


@pytest.mark.basic
def test_authenticate_user_success_and_wrong_password(auth_manager):
    """Аутентификация: верный пароль даёт пользователя, неверный — None."""
    auth_manager.register_user("bob", "secret", "Russia", 500)

    ok_user = auth_manager.authenticate_user("bob", "secret")
    bad_user = auth_manager.authenticate_user("bob", "wrong")

    assert ok_user is not None
    assert ok_user[1] == "bob"
    assert bad_user is None


@pytest.mark.basic
def test_delete_user(auth_manager):
    """Удаление пользователя: после delete_user он не находится по id."""
    auth_manager.register_user("carol", "qwerty", "Kazakhstan", 300)
    assert auth_manager.get_user_by_id(1) is not None

    auth_manager.delete_user(1)

    assert auth_manager.get_user_by_id(1) is None


# ---------------------------------------------------------------------------
# Параметризованные тесты
# ---------------------------------------------------------------------------

@pytest.mark.parametrized
@pytest.mark.parametrize(
    "country, expected_count",
    [
        ("CountryA", 2),
        ("CountryB", 1),
        ("CountryC", 0),
    ],
)
def test_count_users_by_country(auth_manager, country, expected_count):
    """Подсчёт пользователей по стране для разных стран (как в методичке)."""
    auth_manager.register_user("user1", "password123", "CountryA", 1000)
    auth_manager.register_user("user2", "password123", "CountryA", 1000)
    auth_manager.register_user("user3", "password123", "CountryB", 1000)

    assert auth_manager.count_users_by_country(country) == expected_count


@pytest.mark.parametrized
@pytest.mark.parametrize(
    "username, password, expect_found",
    [
        ("dave", "pass", True),        # верная пара
        ("dave", "wrong", False),      # неверный пароль
        ("nobody", "pass", False),     # несуществующий логин
        ("DAVE", "pass", False),       # регистр логина важен
    ],
)
def test_authenticate_user_parametrized(auth_manager, username, password,
                                        expect_found):
    """Аутентификация с разными парами логин/пароль → найден или None."""
    auth_manager.register_user("dave", "pass", "Country", 100)

    user = auth_manager.authenticate_user(username, password)

    assert (user is not None) is expect_found


@pytest.mark.parametrized
@pytest.mark.parametrize(
    "amount, expected_from, expected_to",
    [
        (200, 800, 700),    # пример из методички
        (0, 1000, 500),     # нулевой перевод ничего не меняет
        (1000, 0, 1500),    # перевод всего баланса
        (0.5, 999.5, 500.5),  # дробная сумма
    ],
)
def test_transfer_balance_parametrized(auth_manager, db, amount,
                                       expected_from, expected_to):
    """Перевод разных сумм: балансы отправителя и получателя корректны."""
    auth_manager.register_user("user1", "password123", "CountryA", 1000)
    auth_manager.register_user("user2", "password123", "CountryB", 500)

    auth_manager.transfer_balance(1, 2, amount)

    assert get_balance(db, 1) == expected_from
    assert get_balance(db, 2) == expected_to


# ---------------------------------------------------------------------------
# Тесты исключений
# ---------------------------------------------------------------------------

@pytest.mark.exception
def test_transfer_balance_insufficient_funds(auth_manager, db):
    """Перевод суммы больше баланса → ValueError("Insufficient funds"),
    балансы при этом не меняются."""
    auth_manager.register_user("poor", "p", "Country", 100)
    auth_manager.register_user("rich", "p", "Country", 1000)

    with pytest.raises(ValueError, match="Insufficient funds"):
        auth_manager.transfer_balance(1, 2, 500)

    assert get_balance(db, 1) == 100
    assert get_balance(db, 2) == 1000


@pytest.mark.exception
def test_register_duplicate_username(auth_manager):
    """Повторная регистрация того же username → sqlite3.IntegrityError
    (нарушение ограничения UNIQUE)."""
    auth_manager.register_user("eve", "p1", "Country", 10)

    with pytest.raises(sqlite3.IntegrityError,
                       match="UNIQUE constraint failed"):
        auth_manager.register_user("eve", "p2", "Country", 20)


# ---------------------------------------------------------------------------
# Тесты безопасности: SQL-инъекции
# ---------------------------------------------------------------------------

@pytest.mark.security
def test_sql_injection_authenticate_user(auth_manager):
    """Доказательство уязвимости: authenticate_user с payload
    "admin' OR '1'='1" возвращает пользователя БЕЗ знания пароля."""
    auth_manager.register_user("admin", "supersecret", "Country", 1000)

    # Итоговый SQL: ... WHERE username = 'admin' OR '1'='1' AND password = 'x'
    # AND имеет более высокий приоритет, чем OR, поэтому условие читается как
    # username = 'admin' OR ('1'='1' AND password = 'x') — первая часть
    # истинна, и строка admin возвращается без проверки пароля.
    user = auth_manager.authenticate_user("admin' OR '1'='1", "x")

    assert user is not None
    assert user[1] == "admin"

    # Усиленный payload: "--" комментирует проверку пароля целиком,
    # пользователь возвращается даже без знания логина.
    any_user = auth_manager.authenticate_user("' OR 1=1 --", "x")
    assert any_user is not None
    assert any_user[1] == "admin"

    # Контроль: с обычным неверным паролем доступа нет
    assert auth_manager.authenticate_user("admin", "x") is None


@pytest.mark.security
def test_sql_injection_register_user_drop_table(auth_manager, db):
    """Попытка инъекции "DROP TABLE users" через register_user.

    Фактическое поведение sqlite3: метод execute() выполняет только ОДНО
    выражение, поэтому строка с двумя statement отвергается с
    sqlite3.ProgrammingError ("You can only execute one statement at a
    time"). Таблица users при этом остаётся на месте.
    """
    payload = "x', 'p', 'c', 0); DROP TABLE users; --"

    with pytest.raises(sqlite3.ProgrammingError,
                       match="only execute one statement"):
        auth_manager.register_user(payload, "p", "c", 0)

    cursor = db.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
    )
    tables = cursor.fetchall()
    assert len(tables) == 1  # таблица users всё ещё существует

    # Ни одна строка не вставлена — INSERT не был выполнен
    cursor.execute("SELECT COUNT(*) FROM users")
    assert cursor.fetchone()[0] == 0


# ---------------------------------------------------------------------------
# Пропускаемые тесты
# ---------------------------------------------------------------------------

@pytest.mark.slow
@pytest.mark.skip(reason="Медленный тест: массовая регистрация, "
                         "не запускается в учебном прогоне")
def test_register_many_users(auth_manager):
    """Регистрация 10 000 пользователей (демонстрация @pytest.mark.skip)."""
    for i in range(10_000):
        auth_manager.register_user(f"user{i}", "p", "Country", i)
    assert auth_manager.count_users_by_country("Country") == 10_000


@pytest.mark.skipif(sys.version_info < (3, 7),
                    reason="Требуется Python 3.7+ (упорядоченные dict)")
def test_user_row_to_dict(auth_manager):
    """Преобразование строки пользователя в dict (демонстрация skipif:
    на Python 3.7+ тест выполняется, на более старых — пропускается)."""
    auth_manager.register_user("frank", "p", "Country", 42)
    row = auth_manager.get_user_by_id(1)
    keys = ("id", "username", "password", "country", "balance")

    user = dict(zip(keys, row))

    assert list(user) == list(keys)
    assert user["username"] == "frank"
    assert user["balance"] == 42
