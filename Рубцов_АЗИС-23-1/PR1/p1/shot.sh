#!/bin/bash
# Скриншот окна gnome-calculator (с рамкой openbox) -> p1/screens/<name>.png
# Использование: ./shot.sh <имя_файла_без_расширения>
export DISPLAY=:99
NAME="$1"
WID=$(xdotool search --name '^Калькулятор$' | head -1)
[ -z "$WID" ] && WID=$(xdotool search --class gnome-calculator | tail -1)
# геометрия окна вместе с декорацией openbox
eval $(xdotool getwindowgeometry --shell "$WID" | sed "s/WIDTH/W/;s/HEIGHT/H/")
# заголовок openbox ~ 22px сверху, рамка 1px
PAD_T=0; PAD=0
X0=$((X-PAD)); Y0=$((Y-PAD_T)); W0=$((W+2*PAD)); H0=$((H+PAD_T+PAD))
[ $X0 -lt 0 ] && X0=0; [ $Y0 -lt 0 ] && Y0=0
sleep 0.6
import -window root -crop ${W0}x${H0}+${X0}+${Y0} +repage "/home/claude/work/p1/screens/${NAME}.png"
echo "saved ${NAME}.png (${W0}x${H0}+${X0}+${Y0})"
