# -*- coding: utf-8 -*-
"""Программа продажи кофе (прошивка автомата) — Приложение А.

Интерфейс соответствует утверждённому прототипу (окно MainWindow):
  1. INSERT COINS  — поле ввода суммы и кнопка Insert
  2. SELECT PRODUCT — переключатели Cappuccino / Espresso / Americano / Latte
  3. GET YOUR PRODUCT — сообщения автомата
  4. Goodbye — пожелание хорошего дня
Выбор напитка подтверждается клавишей Enter.
"""
import sys
from PyQt5 import QtWidgets, QtCore


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MainWindow")
        self.resize(596, 429)
        self.balance = 0
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # 1. INSERT COINS
        box1 = QtWidgets.QGroupBox("1. INSERT COINS")
        l1 = QtWidgets.QVBoxLayout(box1)
        self.coinEdit = QtWidgets.QLineEdit("0")
        self.insertBtn = QtWidgets.QPushButton("Insert")
        l1.addWidget(self.coinEdit)
        l1.addWidget(self.insertBtn)
        layout.addWidget(box1)

        # 2. SELECT PRODUCT
        box2 = QtWidgets.QGroupBox("2. SELECT PRODUCT")
        l2 = QtWidgets.QVBoxLayout(box2)
        self.rbCappuccino = QtWidgets.QRadioButton("Cappuccino ---> 35")
        self.rbEspresso = QtWidgets.QRadioButton("Espresso ---> 30")
        self.rbAmericano = QtWidgets.QRadioButton("Americano ---> 35")
        self.rbLatte = QtWidgets.QRadioButton("Latte ---> 40")
        for rb in (self.rbCappuccino, self.rbEspresso, self.rbAmericano, self.rbLatte):
            l2.addWidget(rb)
        layout.addWidget(box2)

        # 3. GET YOUR PRODUCT
        box3 = QtWidgets.QGroupBox("3. GET YOUR PRODUCT")
        l3 = QtWidgets.QVBoxLayout(box3)
        self.productLabel = QtWidgets.QLabel("")
        l3.addWidget(self.productLabel)
        layout.addWidget(box3)

        # 4. Goodbye
        box4 = QtWidgets.QGroupBox("4. Goodbye")
        l4 = QtWidgets.QVBoxLayout(box4)
        self.goodbyeLabel = QtWidgets.QLabel("")
        l4.addWidget(self.goodbyeLabel)
        layout.addWidget(box4)

        self.insertBtn.clicked.connect(self.insert_coins)
        self.coinEdit.returnPressed.connect(self.insert_coins)

    def insert_coins(self):
        # внесение денег
        value = int(self.coinEdit.text())
        self.balance = self.balance + value
        self.productLabel.setText("Inserted: " + str(self.balance))
        self.coinEdit.setText("0")

    def keyPressEvent(self, event):
        # покупка подтверждается клавишей Enter
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            if self.rbCappuccino.isChecked():
                self.buy("Cappuccino", 35)
            elif self.rbEspresso.isChecked():
                self.buy("Espresso", 30)
            elif self.rbAmericano.isChecked():
                self.buy("Americano", 35)
            elif self.rbLatte.isChecked():
                self.buy("Latte", 40)
        super().keyPressEvent(event)

    def buy(self, name, price):
        if self.balance < price:
            self.productLabel.setText("Not enough coins!")
            return
        change = self.balance - price
        self.productLabel.setText("Inserted: " + str(self.balance) + "\nChange: " + str(change)
                                  + "\nYour " + name + " is ready!")
        self.goodbyeLabel.setText("Have a nice day!")
        self.balance = 0
        # через 10 секунд интерфейс обнуляется
        QtCore.QTimer.singleShot(10000, self.reset)

    def reset(self):
        self.balance = 0
        self.coinEdit.setText("0")
        self.productLabel.setText("")
        self.goodbyeLabel.setText("")
        for rb in (self.rbCappuccino, self.rbEspresso, self.rbAmericano, self.rbLatte):
            rb.setAutoExclusive(False)
            rb.setChecked(False)
            rb.setAutoExclusive(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
