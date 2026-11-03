"""Кофейный автомат — учебное приложение для практических работ 1–2.

Реализует спецификацию:
  1. внесение монет/купюр РФ номиналом 1–500 руб. с накоплением суммы;
  2. выбор напитка (Cappuccino / Espresso / Americano / Latte);
  3. выдача напитка, показ внесённой суммы и сдачи;
  4. пожелание хорошего дня и автоматический сброс интерфейса через 10 секунд.
"""

import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

# Допустимые номиналы монет и купюр РФ в рамках спецификации (1–500 руб.)
VALID_DENOMINATIONS = (1, 2, 5, 10, 50, 100, 200, 500)
RESET_DELAY_MS = 10_000

PRODUCTS = {
    "Cappuccino": 35,
    "Espresso": 30,
    "Americano": 35,
    "Latte": 40,
}


class VendingMachine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.balance = 0
        self.reset_timer = QTimer(self)
        self.reset_timer.setSingleShot(True)
        self.reset_timer.timeout.connect(self.reset_interface)

        self.setWindowTitle("Coffee Vending Machine")
        self.setGeometry(120, 120, 560, 560)
        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)

        # 1. Внесение денег
        coins_group = QGroupBox("1. INSERT COINS")
        coins_layout = QVBoxLayout()
        self.coin_input = QLineEdit("0")
        self.coin_input.setPlaceholderText("Введите номинал: 1, 2, 5, 10, 50, 100, 200, 500")
        self.insert_button = QPushButton("Insert")
        self.insert_button.clicked.connect(self.insert_coins)
        self.balance_label = QLabel("Balance: 0 rub.")
        coins_layout.addWidget(self.coin_input)
        coins_layout.addWidget(self.insert_button)
        coins_layout.addWidget(self.balance_label)
        coins_group.setLayout(coins_layout)

        # 2. Выбор напитка
        products_group = QGroupBox("2. SELECT PRODUCT")
        products_layout = QVBoxLayout()
        self.product_buttons = {}
        for name, price in PRODUCTS.items():
            rb = QRadioButton(f"{name} ---> {price}")
            self.product_buttons[name] = rb
            products_layout.addWidget(rb)
        products_group.setLayout(products_layout)

        # 3. Выдача напитка
        product_group = QGroupBox("3. GET YOUR PRODUCT")
        product_layout = QVBoxLayout()
        self.product_label = QLabel("")
        self.product_label.setWordWrap(True)
        self.product_label.setMinimumHeight(75)
        self.product_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        product_layout.addWidget(self.product_label)
        product_group.setLayout(product_layout)

        # 4. Прощание
        goodbye_group = QGroupBox("4. Goodbye")
        goodbye_layout = QVBoxLayout()
        self.goodbye_label = QLabel("")
        self.goodbye_label.setMinimumHeight(45)
        goodbye_layout.addWidget(self.goodbye_label)
        goodbye_group.setLayout(goodbye_layout)

        # Кнопки действий
        buttons_layout = QHBoxLayout()
        self.buy_button = QPushButton("Buy")
        self.buy_button.clicked.connect(self.select_product)
        self.cancel_button = QPushButton("Cancel / Refund")
        self.cancel_button.clicked.connect(self.cancel)
        buttons_layout.addWidget(self.buy_button)
        buttons_layout.addWidget(self.cancel_button)

        main_layout.addWidget(coins_group)
        main_layout.addWidget(products_group)
        main_layout.addWidget(product_group)
        main_layout.addWidget(goodbye_group)
        main_layout.addLayout(buttons_layout)

    # ------------------------------------------------------------- actions
    def insert_coins(self):
        """Принимает очередную монету/купюру и накапливает баланс."""
        raw = self.coin_input.text().strip().replace(",", ".")
        try:
            value = int(raw)
        except ValueError:
            self._show_error("Invalid coin input! Enter an integer value.")
            return

        if value not in VALID_DENOMINATIONS:
            self._show_error(
                "Invalid denomination! Accepted: 1, 2, 5, 10, 50, 100, 200, 500 rub."
            )
            return

        self.balance += value
        self.reset_timer.stop()
        self.goodbye_label.clear()
        self.balance_label.setText(f"Balance: {self.balance} rub.")
        self.product_label.setText(f"Inserted: {self.balance} rub.")

    def select_product(self):
        """Выдаёт выбранный напиток, если средств достаточно."""
        name = self.selected_product()
        if name is None:
            self._show_error("Please select a product!")
            return

        price = PRODUCTS[name]
        if self.balance < price:
            self._show_error(
                f"Not enough coins! {name} costs {price} rub., "
                f"you need {price - self.balance} rub. more."
            )
            return

        change = self.balance - price
        self.product_label.setText(
            f"Product: {name}\n"
            f"Inserted: {self.balance} rub.\n"
            f"Price: {price} rub.\n"
            f"Change: {change} rub."
        )
        self.goodbye_label.setText("Have a nice day!")
        self._set_controls_enabled(False)
        self.reset_timer.start(RESET_DELAY_MS)

    def cancel(self):
        """Возврат внесённых средств и сброс интерфейса."""
        if self.balance:
            self.product_label.setText(f"Refund: {self.balance} rub.")
        else:
            self.product_label.setText("Nothing to refund.")
        self.goodbye_label.setText("Thank you!")
        self.reset_timer.start(RESET_DELAY_MS)

    def reset_interface(self):
        self.balance = 0
        self.coin_input.setText("0")
        self.balance_label.setText("Balance: 0 rub.")
        self.product_label.clear()
        self.goodbye_label.clear()
        for rb in self.product_buttons.values():
            # В эксклюзивной группе радио-кнопку нужно временно вывести
            # из группы, иначе Qt не даёт снять отметку программно.
            rb.setAutoExclusive(False)
            rb.setChecked(False)
            rb.setAutoExclusive(True)
        self._set_controls_enabled(True)
        self.reset_timer.stop()

    # ------------------------------------------------------------- helpers
    def selected_product(self):
        for name, rb in self.product_buttons.items():
            if rb.isChecked():
                return name
        return None

    def _set_controls_enabled(self, enabled):
        self.coin_input.setEnabled(enabled)
        self.insert_button.setEnabled(enabled)
        self.buy_button.setEnabled(enabled)
        self.cancel_button.setEnabled(enabled)
        for rb in self.product_buttons.values():
            rb.setEnabled(enabled)

    def _show_error(self, message):
        self.goodbye_label.clear()
        self.product_label.setText(message)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.select_product()
        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = VendingMachine()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
