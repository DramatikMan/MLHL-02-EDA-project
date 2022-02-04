from datetime import date, datetime, timedelta

import pandas as pd
from sqlalchemy import select

from app.config import CONSECUTIVE_DATES_TO_PARSE, DATES_TO_SKIP
from app.db.config import db_engine
from app.db.helpers import data_is_missing
from app.db.models import City, Flight
from app.loggers import main_task_log
from app.parser import Parser
from app.scraper import Scraper


def main() -> None:
    starting_point = datetime.now()
    today: date = date.today()

    with db_engine.connect() as conn:
        cities: list[tuple[str, str]] = conn.execute(select(City)).all()
        main_task_log.info('Cities loaded.')
        today = date.today()

        for city in cities:
            on_date = today + timedelta(days=DATES_TO_SKIP)
            end_date = on_date + timedelta(days=CONSECUTIVE_DATES_TO_PARSE)

            while on_date < end_date:
                if data_is_missing(
                    parsing_date=today,
                    destination=city[0],
                    departure_date=on_date,
                    conn=conn
                ):
                    scraper = Scraper(destination=city, on_date=on_date)
                    scraper.run()

                    df: pd.DataFrame = Parser.get_dataframe(
                        parsing_date=today,
                        destination=city,
                        on_date=on_date,
                        HTML=scraper.HTML
                    )
                    df.to_sql(
                        name=Flight.__tablename__,
                        con=conn,
                        if_exists='append',
                        index=False
                    )
                else:
                    main_task_log.info(
                        "Today's data for flights to "
                        f'"{city[0]}" on {on_date.isoformat()} '
                        'is already present in the DB. Moving on.'
                    )

                on_date += timedelta(days=1)

    delta: timedelta = datetime.now() - starting_point
    main_task_log.info(f'Task run completed in {delta}. SUCCESS.')


if __name__ == '__main__':
    main()
