from datetime import datetime, timedelta
from sqlalchemy import func, extract

from app import db
from app.models.locations import Location


def serve_stats(start_date):
    start_date_dt = datetime.fromtimestamp(start_date)

    qs = (
        db.session.query(
            extract("minutes", Location.insertion_date).label("m"), func.count("m")
        )
            .filter(Location.insertion_date >= start_date_dt)
            .filter(Location.insertion_date < start_date_dt + timedelta(minutes=5))
            .group_by("m")
            .order_by("m")
    )

    res = {line[0]: line[1] for line in qs.all()}
    db.session.close()
    return res
