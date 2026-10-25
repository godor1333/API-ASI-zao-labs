#!/usr/bin/env python3
"""
Негативный сценарий «расписание на сайте изменилось».

Подменяет data/schedule_current.json, из которого зеркало отвечает на POST /getschedule:
  * Пятница, 3-4 пара «Основы тестирования программного обеспечения»:
      преподаватель Комаров Александр Олегович -> Иванов Иван Иванович,
      аудитория 324 -> 218;
  * добавляется пара в Понедельник (1 пара, «Физическая культура / Пз.»);
  * удаляется 4-я пара во Вторник («Управление ИТ-проектами / Лк.»).

    python3 swap_schedule.py            # подменить
    python3 swap_schedule.py --restore  # вернуть оригинал (data/schedule_original.json)
"""
import copy
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CUR = os.path.join(HERE, "data", "schedule_current.json")
ORIG = os.path.join(HERE, "data", "schedule_original.json")


def restore():
    shutil.copyfile(ORIG, CUR)
    print("restored:", CUR)


def swap():
    with open(ORIG, encoding="utf-8") as f:
        sched = json.load(f)
    changes = []

    # 1. Пятница (wday=5): 3-4 пара — другой преподаватель и аудитория
    for slot in sched["5"]:
        for para in slot:
            if para["predmet_name"].startswith("Основы тестирования"):
                changes.append("Пятница %s: %s %s %s ауд.%s -> Иванов Иван Иванович ауд.218" % (
                    para["para_title"], para["prepod_surname"], para["prepod_name"],
                    para["prepod_initials"], para["aud"]))
                para["prepod_surname"], para["prepod_name"], para["prepod_initials"] = "Иванов", "Иван", "Иванович"
                para["aud"] = "218"

    # 2. Понедельник (wday=1): новая пара
    template = copy.deepcopy(sched["2"][0][0])
    template.update({
        "id": "999901", "wday": "1", "para": "1", "para_title": "1 пара", "para_time": "08:30-10:00",
        "predmet_name": "Физическая культура", "para_type": "Пз.", "aud": "с/з", "comment": "",
        "prepod_surname": "Петров", "prepod_name": "Пётр", "prepod_initials": "Петрович",
    })
    sched["1"] = [[template]]
    changes.append("Понедельник: добавлена 1 пара «Физическая культура / Пз.» Петров Пётр Петрович с/з")

    # 3. Вторник (wday=2): удалить 4-ю пару
    before = len(sched["2"])
    sched["2"] = [slot for slot in sched["2"] if slot[0]["para"] != "4"]
    changes.append("Вторник: удалена 4 пара (было %d пар, стало %d)" % (before, len(sched["2"])))

    # порядок дней: JS перебирает ключи объекта — целочисленные ключи идут по возрастанию
    sched = {k: sched[k] for k in sorted(sched, key=int)}
    with open(CUR, "w", encoding="utf-8") as f:
        json.dump(sched, f, ensure_ascii=False, indent=1)
    print("swapped:", CUR)
    for c in changes:
        print("  -", c)


if __name__ == "__main__":
    restore() if "--restore" in sys.argv else swap()
