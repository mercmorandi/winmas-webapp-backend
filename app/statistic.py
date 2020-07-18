from datetime import datetime, timedelta
from sqlalchemy import func, extract

from app import db
from app.models.locations import Location


def serve_stats(start_date):
    start_date_dt = datetime.fromtimestamp(int(start_date))
    start_date_dt = start_date_dt.replace(second=0, microsecond=0)
    res = {}
    for row in range(start_date_dt.minute, start_date_dt.minute + 5):
        res[row] = 0
    qs = (
        db.session.query(
            extract("minutes", Location.insertion_date).label("m"), func.count("m")
        )
            .filter(Location.insertion_date >= start_date_dt)
            .filter(Location.insertion_date < start_date_dt + timedelta(minutes=5))
            .group_by("m")
            .order_by("m")
    )

    data = {int(line.m): line[1] for line in qs.all()}  # (minute, count)
    res.update(data)

    db.session.close()
    return res
