from datetime import date
from sqlalchemy import text
from sqlalchemy.engine import Connection


def data_is_missing(
    parsing_date: date,
    destination: str,
    departure_date: date,
    conn: Connection
) -> bool:
    is_missing: bool = conn.execute(text(f'''
        SELECT count()
        FROM flight
        WHERE
            parsing_date = '{parsing_date.isoformat()}'
        AND destination = '{destination}'
        AND departure_date = '{departure_date.isoformat()}'
    ''')).scalar() == 0

    return is_missing
