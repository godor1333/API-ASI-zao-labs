"""
Отладка парсера расписания АПИ НГТУ.
Все шаги выполняет get_schedule().
"""

from schedule_parser import ScheduleParser


def main():

    
    print("Период: 07.09.2026 – 18.10.2026")


    parser = ScheduleParser(headless=False)

    try:
        print("\n[1] Получаем расписание (все шаги внутри)...")
        schedule = parser.get_schedule(
            form="Заочная 3 года 10 мес",
            group="АЗИС 23-1",
            date_from="2026-09-07",
            date_to="2026-10-18",
        )
        print(f" Получено {len(schedule)} строк")

        print("\n[2] Тип текущей недели:")
        print(f"    {parser.get_week_type()}")

       
        print("расписание:")

        for i, row in enumerate(schedule, 1):
            print(f"\nСтрока {i}:")
            for j, cell in enumerate(row):
                print(f"  [{j}] {cell!r}")

    except Exception as e:
        print(f"\n ОШИБКА: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    finally:
        #input("\n>>> Нажмите Enter для закрытия браузера...")
        parser.close()
        print("\n Браузер закрыт.")


if __name__ == "__main__":
    main()