from datetime import datetime, timedelta
from sqlalchemy import func, extract

from app import db
from app.models.locations import Location


class StatsDto:
    def __init__(self, minutes, ndevices):
        self.minutes = minutes
        self.nDevice = ndevices

    def __str__(self):
        return self.minutes + ": " + self.nDevice


def serve_stats(start_date):
    start_date_dt = datetime.fromtimestamp(int(start_date))
    start_date_dt = start_date_dt.replace(second=0, microsecond=0)
    res = {}
    for minute in range(5):
        key = start_date_dt + timedelta(minutes=minute)
        res[key.isoformat()] = 0
    qs1 = (
        db.session.query(Location.id)
        .filter(Location.insertion_date >= start_date_dt)
        .filter(Location.insertion_date < start_date_dt + timedelta(minutes=5))
        .distinct(Location.mac_id)
        .subquery()
    )

    qs2 = (
        db.session.query(
            extract("minutes", Location.insertion_date).label("m"), func.count("m")
        )
        .join(qs1, Location.id == qs1.c.id)
        .group_by("m")
        .order_by("m")
    )
    start_date_dt_h = start_date_dt.replace(minute=0)
    print(qs2[0].m)
    data = {
        (start_date_dt_h + timedelta(minutes=int(line.m))).isoformat(): line[1]
        for line in qs2.all()
    }  # (
    # minute, count)
    res.update(data)

    db.session.close()

    #dtoRes = [StatsDto(k, v) for k, v in data.items()]
    #print(str(dtoRes))
    return res
