import sqlite3
import pytest
import sys
import os

from auth_manager import AuthManager



@pytest.fixture
def db():
    """Фикстура: временная БД SQLite в памяти."""
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def auth_manager(db):
    """Фикстура: экземпляр AuthManager с тестовой БД."""
    return AuthManager(db)


@pytest.fixture
def filled_auth_manager(auth_manager):
    """Фикстура: AuthManager с предзаполненными пользователями."""
    auth_manager.register_user("user1", "password123", "CountryA", 1000)
    auth_manager.register_user("user2", "password123", "CountryA", 1000)
    auth_manager.register_user("user3", "password123", "CountryB", 1000)
    return auth_manager




@pytest.mark.basic
def test_register_user(auth_manager):
   
    auth_manager.register_user("alice", "pass123", "CountryA", 500)
    user = auth_manager.authenticate_user("alice", "pass123")
    assert user is not None
    assert user[1] == "alice"
    assert user[3] == "CountryA"
    assert user[4] == 500


@pytest.mark.basic
def test_authenticate_user_success(filled_auth_manager):
    """Базовый тест: успешная аутентификация."""
    user = filled_auth_manager.authenticate_user("user1", "password123")
    assert user is not None
    assert user[1] == "user1"


@pytest.mark.basic
def test_transfer_balance_success(filled_auth_manager):
    """Базовый тест: успешный перевод средств."""
    filled_auth_manager.transfer_balance(1, 2, 300)
    user1 = filled_auth_manager.get_user_by_id(1)
    user2 = filled_auth_manager.get_user_by_id(2)
    assert user1[4] == 700
    assert user2[4] == 1300




@pytest.mark.parametrize("country, expected_count", [
    ("CountryA", 2),
    ("CountryB", 1),
    ("CountryC", 0),
])

def test_count_users_by_country(filled_auth_manager, country, expected_count):
    """Параметризованный тест: подсчёт пользователей по странам."""
    count = filled_auth_manager.count_users_by_country(country)
    assert count == expected_count


@pytest.mark.parametrize("username, password, expected", [
    ("user1", "password123", True),
    ("user1", "wrongpass", False),
    ("nonexistent", "password123", False),
])
def test_authenticate_user_parametrized(filled_auth_manager, username, password, expected):
    """Параметризованный тест: аутентификация с разными данными."""
    user = filled_auth_manager.authenticate_user(username, password)
    assert (user is not None) == expected


@pytest.mark.parametrize("amount, expected_balance", [
    (100, 900),
    (500, 500),
    (1000, 0),
])
def test_transfer_balance_amounts(filled_auth_manager, amount, expected_balance):
    """Параметризованный тест: перевод разных сумм."""
    filled_auth_manager.transfer_balance(1, 2, amount)
    user1 = filled_auth_manager.get_user_by_id(1)
    assert user1[4] == expected_balance




@pytest.mark.exception
def test_transfer_insufficient_funds(filled_auth_manager):
    """Тест исключения: недостаточно средств для перевода."""
    with pytest.raises(ValueError, match="Insufficient funds"):
        filled_auth_manager.transfer_balance(1, 2, 5000)


@pytest.mark.exception
def test_authenticate_nonexistent_user(filled_auth_manager):
    """Тест исключения: аутентификация несуществующего пользователя."""
    user = filled_auth_manager.authenticate_user("ghost", "nopass")
    assert user is None



@pytest.mark.security
@pytest.mark.sql_injection
def test_sql_injection_login(filled_auth_manager):
    """
    Тест SQL-инъекции: аутентификация.
    """
 
    malicious_username = "' OR '1'='1"
    malicious_password = "' OR '1'='1"

    user = filled_auth_manager.authenticate_user(
        malicious_username, malicious_password
    )

    assert user is not None, "SQL-инъекция"


@pytest.mark.security
@pytest.mark.sql_injection
def test_sql_injection_delete(filled_auth_manager):
    """
    Тест SQL-инъекции: попытка удалить всех пользователей
    через user_id.
    """

    malicious_id = "1 OR 1=1"
    filled_auth_manager.delete_user(malicious_id)
    user = filled_auth_manager.get_user_by_id(1)
    assert user is None, "SQL-инъекция должна удалить пользователя"


@pytest.mark.security
@pytest.mark.sql_injection
def test_sql_injection_safe_parameterization(filled_auth_manager):
    """
    Демонстрация: если бы использовалась параметризация,
    инъекция не сработала бы.
    """
    # Безопасный запрос с параметрами
    cursor = filled_auth_manager.connection.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        ("' OR '1'='1", "' OR '1'='1")
    )
    user = cursor.fetchone()
    # При параметризации инъекция не работает
    assert user is None, "Параметризованный запрос защищён от инъекции"




@pytest.mark.skip(reason="Функциональность ещё не реализована")
def test_future_feature():
    """Тест, который пропускается."""
    assert False


@pytest.mark.skipif(sys.version_info < (3, 7), reason="Требуется Python 3.7+")
def test_python_version():
    """Тест, пропускаемый на старых версиях Python."""
    assert True

@pytest.mark.skipif(
    not os.path.exists("config.json"),
    reason="Нет файла конфигурации config.json в папке проекта"
)
def test_with_config():
    """Тест, требующий файла config.json в папке проекта."""
    assert True

# МЕТКИ 
# @pytest.mark.basic      — базовые тесты
# @pytest.mark.exception  — тесты исключений
# @pytest.mark.security   — тесты безопасности
# @pytest.mark.sql_injection — тесты SQL-инъекций