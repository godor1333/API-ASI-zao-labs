

import pytest



WRONG_SCHEDULE = [
    [
        "1 пара / 08:30-10:00",
        "Философия / Лк.",
        "Неизвестный Н.Н.",
        "101",
        "",
        "Нечетная",
    ],
    [
        "2 пара / 10:10-11:40",
        "История / Сем.",
        "Другой Д.Д.",
        "202",
        "",
        "Нечетная",
    ],
]


class TestWrongSchedule:
    

    def test_wrong_schedule_fails(self, real_schedule):
        
        assert real_schedule == WRONG_SCHEDULE, (
            f"\n ТЕСТ ПРОВАЛЕН!"
            f"\n Ожидалось (неверное): {WRONG_SCHEDULE}"
            f"\n Получено (реальное):  {real_schedule}"
        )