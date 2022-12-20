import time
from datetime import datetime

import pandas as pd
import sqlite3
import xmltodict
import requests


class CurrencyScraper:
    """Класс для представления скрапера валют.

    Attributes:
        currency_to_code (dict): (class attribute) Словарь для конвертации идентификатора валюты в код
    """

    currency_to_code = {"BYR": "R01090", "USD": "R01235", "EUR": "R01239", "KZT": "R01335", "UAH": "R01720",
                        "AZN": "R01020", "KGS": "R01370", "UZS": "R01717"}

    @staticmethod
    def get_currency_info_by_date(year: int, month: int, currency: str) -> dict:
        """Возвращает информацию о валюте в указанный месяц и год.

        Args:
            year (int): Год
            month (int): Месяц
            currency (str): Идентификатор валюты

        Returns:
            dict: Информация о валюте
        """
        if month != 1:
            begin_date_str = datetime(year, month - 1, 1).strftime(r"%d/%m/%Y")
        else:
            begin_date_str = datetime(year - 1, 12, 1).strftime(r"%d/%m/%Y")
        end_date_str = datetime(year, month, 1).strftime(r"%d/%m/%Y")
        code = CurrencyScraper.currency_to_code[currency]
        url = f"https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={begin_date_str}&date_req2={end_date_str}&VAL_NM_RQ={code}"
        response = requests.get(url)
        response.close()
        data = xmltodict.parse(response.content)
        if "ValCurs" in data:
            if "Record" in data["ValCurs"]:
                if isinstance(data["ValCurs"]["Record"], dict):
                    return data["ValCurs"]["Record"]
                return data["ValCurs"]["Record"][-1]

    @staticmethod
    def get_currency_value_by_month_year(year: int, month: int, currency: str) -> float:
        """Возвращает курс валюты по отношению к рублю в указанный месяц и год.

        Args:
            date (datetime): Дата
            currency (str): Идентификатор валюты

        Returns:
            float: Курс валюты
        """
        info = CurrencyScraper.get_currency_info_by_date(year, month, currency)
        result = float(info["Value"].replace(',', '.')) / float(info["Nominal"].replace(',', '.'))
        return round(result, 7)

    @staticmethod
    def get_month_range_day(start=None, periods=None) -> pd.Index:
        """Возвращает Index, состоящий из указанного количества дат с таким же номером дня, как
        и в указанной дате, с промежутками в 1 месяц, отформатированный в строку вида "год-месяц"

        Args:
            start (str): Дата начала промежутка в формате d/m/Y
            periods (int): Необходимое количество месяцев

        Returns:
            DatetimeIndex: Промежуток дат с промежутком в месяц
        """
        start_date = pd.Timestamp(start).date()
        month_range = pd.date_range(start=start_date, periods=periods, freq='M')
        month_day = month_range.day.values
        month_day[start_date.day < month_day] = start_date.day
        return pd.to_datetime(month_range.year * 10000 + month_range.month * 100 + month_day, format='%Y%m%d').strftime(
            "%Y-%m")

    @staticmethod
    def get_month_count_between_two_dates(d1: datetime, d2: datetime) -> int:
        """Возвращает количество месяцев между двумя датами.

        Args:
            d1 (datetime): Первая дата
            d2 (datetime): Вторая дата

        Returns:
            int: Количество месяцев между двумя датами
        """
        return abs((d1.year - d2.year) * 12 + d1.month - d2.month)

    @staticmethod
    def parse_to_sqlite(begin_date: datetime, end_date: datetime, db_filename: str):
        """Выгружает курсы валют в интервале между указанными датами и сохраняет результат в виде sqlite файла.

        Args:
            begin_date (datetime): Дата, с которой необходимо выгрузить курсы валют
            end_date (datetime): Дата, до которой необходимо выгрузить курсы валют
            db_filename (str): Имя sqlite файла результата
        """
        currencies = {}
        for year in range(begin_date.year, end_date.year + 1):
            if year == begin_date.year == end_date.year:
                months = range(begin_date.month, end_date.month + 1)
            elif year == begin_date.year:
                months = range(begin_date.month, 12 + 1)
            elif year == end_date.year:
                months = range(1, end_date.month + 1)
            else:
                months = range(1, 12 + 1)
            for month in months:
                for currency in CurrencyScraper.currency_to_code:
                    if currency not in currencies:
                        currencies[currency] = []
                    print(f"Получение информации за год: {year}, месяц: {month}, валюту: {currency}")
                    currency_value = CurrencyScraper.get_currency_value_by_month_year(year, month, currency)
                    currencies[currency].append(currency_value)
                    time.sleep(0.03)
        df = pd.DataFrame(currencies, index=CurrencyScraper.get_month_range_day(begin_date.strftime(r"%d/%m/%Y"),
                                                                CurrencyScraper.get_month_count_between_two_dates(begin_date,
                                                                                                  end_date) + 1))
        df.index.name = "date"
        conn = sqlite3.connect(db_filename)
        df.to_sql(name="exchange_rate", con=conn)
        conn.close()


begin_date = datetime(2003, 1, 1)
end_date = datetime(2022, 12, 1)
CurrencyScraper.parse_to_sqlite(begin_date, end_date, "exchange_rate.sqlite")
