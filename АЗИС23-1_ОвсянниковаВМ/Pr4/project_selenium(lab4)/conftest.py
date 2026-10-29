import pytest
from schedule_parser import ScheduleParser



DATE_FROM = "2026-09-07"
DATE_TO = "2026-10-18"


@pytest.fixture(scope="module")
def parser():
    p = ScheduleParser(headless=True)
    yield p
    p.close()


@pytest.fixture(scope="module")
def real_schedule(parser):
    return parser.get_schedule(
        form="Заочная 3 года 10 мес",
        group="АЗИС 23-1",
        date_from=DATE_FROM,
        date_to=DATE_TO,
    )


@pytest.fixture(scope="module")
def week_type(parser):
    parser.open_page()
    return parser.get_week_type()