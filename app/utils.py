from datetime import datetime


def date_parser(date):
    return datetime.fromtimestamp(int(date)).replace(second=0, microsecond=0)
