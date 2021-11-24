from datetime import date, datetime, timedelta

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine.cursor import LegacyCursorResult

from .db.config import db_engine
from .loggers import main_task_log
from .parser import Parser
from .scraper import Scraper


def main() -> None:
    starting_point = datetime.now()
    today: date = date.today()

    with db_engine.connect() as conn:
        result: LegacyCursorResult = conn.execute(text('SELECT * FROM city'))
        main_task_log.info('Cities loaded.')
        city: tuple[str, str]

        for city in result:
            for i in range(7):
                on_date = today + timedelta(days=8 + i)
                scraper = Scraper(destination=city, on_date=on_date)
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

    delta: timedelta = starting_point - datetime.now()
    main_task_log.info(f'Task run completed in {delta}. SUCCESS.')


if __name__ == '__main__':
    main()
