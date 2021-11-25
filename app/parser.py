import re
from collections.abc import Callable
from datetime import date
from typing import Optional, Union

import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Tag


class Parser:
    @staticmethod
    def get_airlines(card: Tag) -> str:
        airlines: str = card \
            .find(class_=re.compile('LogoImage_container')) \
            .find('span').text.strip()

        return airlines

    @staticmethod
    def get_departure_time(card: Tag) -> str:
        departure_time: str = card \
            .find(class_=re.compile('LegInfo_routePartialDepart')) \
            .find(class_=re.compile('LegInfo_routePartialTime')) \
            .find('span').text.strip()

        return departure_time

    @staticmethod
    def get_arrival_time(card: Tag) -> str:
        arrival_time: str = card \
            .find(class_=re.compile('LegInfo_routePartialArrive')) \
            .find(class_=re.compile('LegInfo_routePartialTime')) \
            .find('span').text.strip()

        return arrival_time

    @staticmethod
    def get_duration(card: Tag) -> int:
        duration_text: str = card \
            .find(class_=re.compile('Duration_duration')) \
            .text.strip()

        matches: list[str] = re.findall(r'\d+(?=\s)', duration_text)
        duration_in_minutes = int(matches[0]) * 60 \
            + int(matches[1] if len(matches) == 2 else 0)

        return duration_in_minutes

    @staticmethod
    def get_departure_airport(card: Tag) -> str:
        departure_airport: str = card \
            .find(class_=re.compile('LegInfo_routePartialDepart')) \
            .find(class_=re.compile('LegInfo_routePartialCityTooltip')) \
            .text.strip()

        return departure_airport

    @staticmethod
    def get_arrival_airport(card: Tag) -> str:
        arrival_airport: str = card \
            .find(class_=re.compile('LegInfo_routePartialArrive')) \
            .find(class_=re.compile('LegInfo_routePartialCityTooltip')) \
            .text.strip()

        return arrival_airport

    @staticmethod
    def get_min_price(card: Tag) -> int:
        min_price: str = card \
            .find(class_=re.compile('Price_mainPriceContainer')) \
            .find('span').text.strip()

        min_price = re.sub(r'\D', '', min_price)

        return int(min_price)

    @staticmethod
    def get_stops_count(card: Tag) -> int:
        stops_count_text: str = card \
            .find(class_=re.compile('LegInfo_stopsLabelContainer')) \
            .find('span').text.strip()

        if re.match(r'\d', stops_count_text) is not None:
            stops_count = int(stops_count_text.split(' ')[0])
        else:
            stops_count = 0

        return stops_count

    @classmethod
    def get_dataframe(
        cls,
        destination: tuple[str, str],
        on_date: date,
        HTML: Optional[str]
    ) -> pd.DataFrame:
        df_out = pd.DataFrame(columns=[
            'destination', 'parsing_date', 'departure_date', 'days_until',
            'airlines', 'departure_time', 'arrival_time', 'duration_m',
            'departure_airport', 'arrival_airport',
            'min_price', 'stops_count'
        ])

        if HTML is not None:
            soup = BeautifulSoup(HTML, 'html.parser')

            col_x_func: dict[str, Callable[[Tag], Union[str, int]]] = {
                'airlines': cls.get_airlines,
                'departure_time': cls.get_departure_time,
                'arrival_time': cls.get_arrival_time,
                'duration_m': cls.get_duration,
                'departure_airport': cls.get_departure_airport,
                'arrival_airport': cls.get_arrival_airport,
                'min_price': cls.get_min_price,
                'stops_count': cls.get_stops_count
            }

            df: pd.DataFrame = pd.concat(
                [
                    pd.DataFrame(
                        [[getter(child) for getter in col_x_func.values()]],
                        columns=col_x_func.keys()
                    )
                    for child in soup.children
                    if not (
                        child.has_attr('id') or
                        child.has_attr('class') or
                        child.find(class_=re.compile('InlineBrandBanner_link'))
                    )
                ],
                ignore_index=True
            )

            today: date = date.today()
            df['destination'] = destination[0]
            df['parsing_date'] = today
            df['departure_date'] = on_date
            df['days_until'] = (on_date - today).days

            df = df.reindex(columns=[*df.columns[-4:], *df.columns[:-4]])
            df_out = pd.concat([df_out, df])

        return df_out
