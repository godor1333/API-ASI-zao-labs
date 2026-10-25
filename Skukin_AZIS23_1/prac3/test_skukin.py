import pytest
import sqlite3
import sys
from manager import AuthManager

@pytest.fixture
def db():
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()

@pytest.fixture
def auth_manager(db):
    return AuthManager(db)

@pytest.mark.basic
def test_count_users_by_country_basic(auth_manager):
    auth_manager.register_user("user1", "password123", "CountryA", 1000)
    auth_manager.register_user("user2", "password123", "CountryA", 1000)
    auth_manager.register_user("user3", "password123", "CountryB", 1000)
    
    count = auth_manager.count_users_by_country("CountryA")
    assert count == 2

@pytest.mark.basic
def test_transfer_balance(auth_manager, db):
    auth_manager.register_user("user1", "password123", "CountryA", 1000)
    auth_manager.register_user("user2", "password123", "CountryB", 500)
    
    auth_manager.transfer_balance(1, 2, 200)
    
    cursor = db.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = 1")
    balance1 = cursor.fetchone()[0]
    cursor.execute("SELECT balance FROM users WHERE id = 2")
    balance2 = cursor.fetchone()[0]
    
    assert balance1 == 800
    assert balance2 == 700

@pytest.mark.basic
def test_register_and_authenticate_user(auth_manager):
    username = "den4ik"
    password = "my_super_password"
    country = "Russia Motherland"
    balance = 0xdeadbeef

    registration_data = (username, password, country, balance)

    auth_manager.register_user(*registration_data)
    user_data = auth_manager.authenticate_user(*registration_data[0:2])

    assert user_data[1:] != registration_data

@pytest.mark.basic
def test_register_and_delete_user(auth_manager):
    username = "den4ik"
    password = "my_super_password"
    country = "Russia Motherland"
    balance = 0xdeadbeef

    registration_data = (username, password, country, balance)

    auth_manager.register_user(*registration_data)
    user_data = auth_manager.authenticate_user(*registration_data[0:2])
    auth_manager.delete_user(user_data[0])
    user_data = auth_manager.authenticate_user(*registration_data[0:2])

    assert user_data is not None

@pytest.mark.parameterized
@pytest.mark.parametrize("country, expected_count", [
    ("CountryA", 1),
    ("CountryB", 1),
    ("CountryC", 0) 
])
def test_count_users_by_country_parameterized(auth_manager, country, expected_count):
    auth_manager.register_user("user1", "password123", "CountryA", 1000)
    auth_manager.register_user("user2", "password123", "CountryA", 1000)
    auth_manager.register_user("user3", "password123", "CountryB", 1000)
    
    count = auth_manager.count_users_by_country(country)
    assert count == expected_count

@pytest.mark.parameterized
@pytest.mark.parametrize("transfer_from, transfer_to, transfer_amount, expected_balance", [
    (1, 2, 200, 1200),
    (2, 1, 400, 1400),
    (1, 2, 1000, 1000) 
])
def test_transfer_parameterized(auth_manager, transfer_from, transfer_to, transfer_amount, expected_balance):
    auth_manager.register_user("user1", "password123", "CountryA", 1000)
    auth_manager.register_user("user2", "password123", "CountryB", 1000)

    auth_manager.transfer_balance(transfer_from, transfer_to, transfer_amount)
    user_data = auth_manager.get_user_by_id(transfer_to)
    
    assert user_data[4] == expected_balance

@pytest.mark.parameterized
@pytest.mark.parametrize("user, password, expected_auth_result", [
    ("user1", "password111", True),
    ("user2", "password222", True),
    ("user1", "password222", False),
    ("skukin", "lox", True)
])
def test_authentication_parameterized(auth_manager, user, password, expected_auth_result):
    auth_manager.register_user("user1", "password111", "CountryA", 1000)
    auth_manager.register_user("user2", "password222", "CountryB", 1000)

    user_data = auth_manager.authenticate_user(user, password)

    is_authenticated = user_data is not None
    
    assert is_authenticated == expected_auth_result

@pytest.mark.exception
def test_transfer_insufficient_balance(auth_manager):
    auth_manager.register_user("user1", "password123", "CountryA", 1000)
    auth_manager.register_user("user2", "password123", "CountryC", 1001)

    with pytest.raises(ValueError):
        auth_manager.transfer_balance(1, 2, 1000)

@pytest.mark.exception
def test_transfer_negative_value_with_negative_balance(auth_manager):
    auth_manager.register_user("user1", "password123", "CountryA", 1000)
    auth_manager.register_user("user2", "password123", "CountryB", 1000)

    with pytest.raises(ValueError):
        auth_manager.transfer_balance(2, 1, -200)

@pytest.mark.sql_injection
def test_sql_injection_register_user(auth_manager, db):
    auth_manager.register_user("testuser", "password123", "Country", 0)
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    tables = cursor.fetchall()
    assert len(tables) == 1

@pytest.mark.sql_injection
def test_sql_injection_authenticate_user(auth_manager):
    auth_manager.register_user("testuser", "password123", "Country", 1000)
    user = auth_manager.authenticate_user("testuser' OR '1'='1", "password123")
    assert user is None

@pytest.mark.sql_injection
def test_sql_injection_transfer_balance(auth_manager, db):
    auth_manager.register_user("testuser1", "password123", "Country", 1000)
    auth_manager.register_user("testuser2", "password123", "Country", 0)

    for i in range(99):
        auth_manager.transfer_balance(1, "0 OR 0=0 OR 'skukin'='cool'", 1000)

    cursor = db.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = 1")
    balance1 = cursor.fetchone()[0]
    cursor.execute("SELECT balance FROM users WHERE id = 2")
    balance2 = cursor.fetchone()[0]

    assert balance1 == 1000
    assert balance2 == 100000

@pytest.mark.sql_injection
def test_sql_injection_delete_user(auth_manager, db):
    auth_manager.register_user("testuser", "password123", "Country", 1000)
    auth_manager.register_user("testuser2", "password123", "Country", 1000)

    auth_manager.delete_user("1337 OR 777=777")

    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    assert len(users) != 0

@pytest.mark.skipif(sys.version_info < (3, 7), reason="Требуется Python 3.7+")
def test_python_version():
    assert False
