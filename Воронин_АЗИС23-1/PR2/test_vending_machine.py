"""Тесты логики кофейного автомата (чёрный ящик + проверка реализации)."""

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5.QtWidgets import QApplication

from vending_machine import PRODUCTS, VendingMachine


@pytest.fixture(scope="session")
def app():
    application = QApplication.instance() or QApplication(sys.argv)
    yield application


@pytest.fixture
def machine(app):
    window = VendingMachine()
    yield window
    window.close()


def insert(machine, value):
    machine.coin_input.setText(str(value))
    machine.insert_coins()


# ---------------------------------------------------------------- deposit
@pytest.mark.parametrize("coin", [1, 2, 5, 10, 50, 100, 200, 500])
def test_valid_denominations_are_accepted(machine, coin):
    insert(machine, coin)
    assert machine.balance == coin


def test_coins_are_accumulated(machine):
    insert(machine, 100)
    insert(machine, 50)
    insert(machine, 10)
    assert machine.balance == 160
    assert "160" in machine.balance_label.text()


@pytest.mark.parametrize("coin", [0, 3, 7, 25, 501, -1, 1000])
def test_invalid_denominations_are_rejected(machine, coin):
    insert(machine, coin)
    assert machine.balance == 0
    assert "Invalid denomination" in machine.product_label.text()


def test_non_numeric_input_is_rejected(machine):
    machine.coin_input.setText("abc")
    machine.insert_coins()
    assert machine.balance == 0
    assert "Invalid coin input" in machine.product_label.text()


# ---------------------------------------------------------------- purchase
def test_exact_payment_dispenses_product(machine):
    for coin in (10, 10, 10, 5):
        insert(machine, coin)
    machine.product_buttons["Cappuccino"].setChecked(True)
    machine.select_product()

    assert "Product: Cappuccino" in machine.product_label.text()
    assert "Change: 0" in machine.product_label.text()
    assert machine.goodbye_label.text() == "Have a nice day!"


def test_purchase_with_change(machine):
    insert(machine, 100)
    machine.product_buttons["Latte"].setChecked(True)
    machine.select_product()

    assert "Inserted: 100" in machine.product_label.text()
    assert "Price: 40" in machine.product_label.text()
    assert "Change: 60" in machine.product_label.text()


def test_insufficient_funds(machine):
    insert(machine, 10)
    insert(machine, 10)
    machine.product_buttons["Espresso"].setChecked(True)
    machine.select_product()

    assert "Not enough coins" in machine.product_label.text()
    assert "10" in machine.product_label.text()  # сколько не хватает
    assert machine.balance == 20


def test_product_not_selected(machine):
    insert(machine, 100)
    machine.select_product()

    assert "select a product" in machine.product_label.text().lower()
    assert machine.balance == 100


# ------------------------------------------------------------------ reset
def test_interface_resets_after_dispense(machine):
    insert(machine, 50)
    machine.product_buttons["Americano"].setChecked(True)
    machine.select_product()

    assert machine.reset_timer.isActive()

    machine.reset_interface()

    assert machine.balance == 0
    assert machine.product_label.text() == ""
    assert machine.goodbye_label.text() == ""
    assert machine.selected_product() is None
    assert machine.coin_input.isEnabled()


def test_cancel_returns_money(machine):
    insert(machine, 100)
    machine.cancel()

    assert "Refund: 100" in machine.product_label.text()
    assert machine.reset_timer.isActive()
