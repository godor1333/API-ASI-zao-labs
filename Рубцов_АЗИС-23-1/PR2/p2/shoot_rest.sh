#!/bin/bash
# Оставшиеся сценарии (после аварийного завершения приложения в TC-004 X-сервер пришлось перезапустить)
cd "$(dirname "$0")"
export DISPLAY=:97 QT_QPA_PLATFORM=xcb
Xvfb :97 -screen 0 1024x768x24 >/dev/null 2>&1 &
sleep 1; openbox >/dev/null 2>&1 & sleep 1
source <(sed -n '/^start_app()/,/^insert()/p' shoot.sh)
# TC-005: Latte за 40 при балансе 50 -> сдача 10; затем проверка обнуления через 10 с
start_app tc005; insert 50; click_radio 225; xdotool key Return; shot tc005_p_latte; sleep 10.5; shot tc005_p_reset
# Espresso 30 при 30
start_app tc_esp; insert 10; insert 10; insert 10; click_radio 167; xdotool key Return; shot tc_espresso_30
# Americano при 35, затем повторное нажатие Enter без денег (баланс обнулён) -> Not enough coins!
start_app tc_amer; insert 35; click_radio 196; xdotool key Return; shot tc_americano_35; xdotool key Return; shot tc_americano_second_enter
pkill -f "python3 coffee_mach[i]ne.py" >/dev/null 2>&1
echo DONE
