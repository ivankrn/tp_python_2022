import time
from datetime import datetime

import pandas as pd
import xmltodict
import requests


class CurrencyScraper:
    """Класс для представления скрапера валют.

    Attributes:
        currency_to_code (dict): (class attribute) Словарь для конвертации идентификатора валюты в код
    """

    currencies_to_parse = ["BYR", "USD", "EUR", "KZT", "UAH", "AZN", "KGS", "UZS"]

    @staticmethod
    def get_exchange_rate_by_date(year: int, month: int) -> dict:
        """Возвращает курсы валют в указанный месяц и год.

        Args:
            year (int): Год
            month (int): Месяц

        Returns:
            dict: Курсы необходимых валют в указанный месяц и год
        """
        date_str = datetime(year, month, 1).strftime(r"%d/%m/%Y")
        url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}&d=0"
        response = requests.get(url)
        response.close()
        data = xmltodict.parse(response.content)
        valutes = data["ValCurs"]["Valute"]
        exchange_rate = {}
        for valute in valutes:
            currency = valute["CharCode"]
            if currency in CurrencyScraper.currencies_to_parse:
                valute_value = float(valute["Value"].replace(',', '.'))
                valute_nominal = float(valute["Nominal"].replace(',', '.'))
                exchange_rate[currency] = round(valute_value / valute_nominal, 8)
        for currency in CurrencyScraper.currencies_to_parse:
            if currency not in exchange_rate:
                exchange_rate[currency] = None
        return exchange_rate

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
    def parse_to_csv(begin_date: datetime, end_date: datetime, csv_filename: str):
        """Выгружает курсы валют в интервале между указанными датами и сохраняет результат в виде csv файла.

        Args:
            begin_date (datetime): Дата, с которой необходимо выгрузить курсы валют
            end_date (datetime): Дата, до которой необходимо выгрузить курсы валют
            csv_filename (str): Имя csv файла результата
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
                print(f"Получение курсов валют за {year} год, {month} месяц")
                exchange_rate = CurrencyScraper.get_exchange_rate_by_date(year, month)
                for currency in exchange_rate:
                    if currency not in currencies:
                        currencies[currency] = []
                    currencies[currency].append(exchange_rate[currency])
                time.sleep(0.03)
        df = pd.DataFrame(currencies, index=CurrencyScraper.get_month_range_day(begin_date.strftime(r"%d/%m/%Y"),
                                                                CurrencyScraper.get_month_count_between_two_dates(begin_date,
                                                                                                  end_date) + 1))
        df.index.name = "date"
        df.to_csv(csv_filename, encoding="utf-8")


begin_date = datetime(2003, 1, 1)
end_date = datetime(2022, 12, 1)
CurrencyScraper.parse_to_csv(begin_date, end_date, "exchange_rate.csv")
