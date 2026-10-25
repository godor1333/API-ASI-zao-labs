#!/bin/bash
# Запуск gnome-calculator под Xvfb :99 с русской локалью и собственной сеансовой шиной D-Bus
# (без D-Bus dconf не сохраняет настройки — переключатели формата/точности не срабатывают).
export DISPLAY=:99 GDK_BACKEND=x11 LANG=ru_RU.UTF-8 LC_ALL=ru_RU.UTF-8 LANGUAGE=ru
exec dbus-run-session -- gnome-calculator
