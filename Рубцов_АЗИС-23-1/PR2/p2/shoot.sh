#!/bin/bash
# Снятие реальных скриншотов приложения coffee_machine.py под Xvfb.
# Каждый сценарий: перезапуск приложения, ввод через xdotool, скриншот окна.
set +e
cd "$(dirname "$0")"
mkdir -p screens
export DISPLAY=:97
export QT_QPA_PLATFORM=xcb
pkill -f "Xvfb :97" >/dev/null 2>&1 || true
Xvfb :97 -screen 0 1024x768x24 >/dev/null 2>&1 &
sleep 1
openbox >/dev/null 2>&1 &
sleep 1

start_app() {
  pkill -f "python3 coffee_mach[i]ne.py" >/dev/null 2>&1 || true
  sleep 0.5
  python3 coffee_machine.py > "screens/log_$1.txt" 2>&1 &
  APP_PID=$!
  for i in $(seq 1 30); do
    WID=$(xdotool search --name '^MainWindow$' 2>/dev/null | head -1)
    [ -n "$WID" ] && break
    sleep 0.3
  done
  xdotool windowmove "$WID" 200 150
  xdotool windowactivate --sync "$WID"
  sleep 0.7
  eval "$(xdotool getwindowgeometry --shell "$WID")"   # X, Y, WIDTH, HEIGHT клиентской области
  echo "window $WID at $X,$Y ${WIDTH}x${HEIGHT}"
}

shot() {  # shot NAME
  sleep 0.6
  import -frame -window "$WID" "screens/$1.png"
  echo "saved screens/$1.png"
}

# координаты внутри окна (клиентская область начинается ниже заголовка openbox)
# координаты относительно клиентской области окна: поле ввода +33, Insert +64, радио: Cappuccino +138, Espresso +167, Americano +196, Latte +225
click_edit()   { xdotool mousemove $((X+300)) $((Y+33)) click 1; sleep 0.2; xdotool key ctrl+a; }
click_insert() { xdotool mousemove $((X+300)) $((Y+64)) click 1; sleep 0.3; }
click_radio()  { xdotool mousemove $((X+27)) $((Y+$1)) click 1; sleep 0.3; }
insert() { click_edit; xdotool type --delay 40 -- "$1"; click_insert; }

# 0. исходное состояние
start_app 00_initial; shot 00_initial

# TC-001-P1: баланс 35, Cappuccino
start_app tc001_p1; insert 35; shot tc001_p1_inserted; click_radio 138; xdotool key Return; shot tc001_p1_result

# TC-001-P2: баланс 36 (10+10+10+5+1), Cappuccino -> сдача 1
start_app tc001_p2; insert 10; insert 10; insert 10; insert 5; insert 1; shot tc001_p2_inserted; click_radio 138; xdotool key Return; shot tc001_p2_result

# TC-001-N1: баланс 34, Cappuccino -> Not enough coins!
start_app tc001_n1; insert 10; insert 10; insert 10; insert 2; insert 2; click_radio 138; xdotool key Return; shot tc001_n1_result

# TC-001-N2: баланс 0
start_app tc001_n2; click_radio 138; xdotool key Return; shot tc001_n2_result

# TC-001-N3: баланс 1
start_app tc001_n3; insert 1; click_radio 138; xdotool key Return; shot tc001_n3_result

# TC-002: внесение монеты 500 (граница) и 501 (за границей допустимого)
start_app tc002_500; insert 500; shot tc002_p_500
start_app tc002_501; insert 501; shot tc002_n_501
start_app tc002_0; insert 0; shot tc002_n_0
start_app tc002_neg; insert -5; shot tc002_n_neg

# TC-003: несуществующий номинал 3 руб.
start_app tc003_3; insert 3; shot tc003_n_3

pkill -f "python3 coffee_mach[i]ne.py" >/dev/null 2>&1 || true
echo DONE
