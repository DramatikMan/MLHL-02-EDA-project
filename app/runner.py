from datetime import date, timedelta

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine.cursor import LegacyCursorResult

from .db.config import db_engine
from .loggers import main_task_log
from .parser import Parser
from .scraper import Scraper


def main() -> None:
    today: date = date.today()

    with Scraper() as scraper, db_engine.connect() as conn:
        result: LegacyCursorResult = conn.execute(text('SELECT * FROM city'))
        main_task_log.info('Cities loaded.')
        city: tuple[str, str]

        for city in result:
            scraper.set_destination(value=city)

            for i in range(7):
                on_date = today + timedelta(days=8 + i)
                scraper.set_on_date(value=on_date)
                scraper.run()

                df: pd.DataFrame = Parser.get_dataframe(
                    destination=city,
                    on_date=on_date,
                    HTML=scraper.HTML
                )
                df.to_sql(
                    name='flight',
                    con=conn,
                    if_exists='append',
                    index=False
                )

    main_task_log.info('Task run is done. SUCCESS.')


if __name__ == '__main__':
    main()
