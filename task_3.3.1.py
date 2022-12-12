import time
from datetime import datetime

import pandas as pd
import xmltodict
import requests

currency_to_code = {"BYR": "R01090", "USD": "R01235", "EUR": "R01239", "KZT": "R01335", "UAH": "R01720"}


def get_currency_info_by_date(date: datetime, currency: str) -> dict:
    """Возвращает информацию о валюте на указанную дату.

    Args:
        date (datetime): Дата
        currency (str): Идентификатор валюты

    Returns:
        dict: Информация о валюте
    """
    date_str = date.strftime(r"%d/%m/%Y")
    code = currency_to_code[currency]
    url = f"https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={date_str}&date_req2={date_str}&VAL_NM_RQ={code}"
    response = requests.get(url).content
    data = xmltodict.parse(response)
    if "ValCurs" in data:
        if "Record" in data["ValCurs"]:
            return data["ValCurs"]["Record"]
    return {"Value": "0", "Nominal": "1"}


def get_currency_value_by_date(date: datetime, currency: str) -> float:
    """Возвращает курс валюты по отношению к рублю на указанную дату.

    Args:
        date (datetime): Дата
        currency (str): Идентификатор валюты

    Returns:
        float: Курс валюты
    """
    info = get_currency_info_by_date(date, currency)
    result = float(info["Value"].replace(',', '.')) / float(info["Nominal"].replace(',', '.'))
    return round(result, 7)


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


def get_month_count_between_two_dates(d1: datetime, d2: datetime) -> int:
    """Возвращает количество месяцев между двумя датами.

    Args:
        d1 (datetime): Первая дата
        d2 (datetime): Вторая дата

    Returns:
        int: Количество месяцев между двумя датами
    """
    return abs((d1.year - d2.year) * 12 + d1.month - d2.month)


begin_date = datetime(2003, 1, 24)
end_date = datetime(2022, 7, 19)
currencies = {}
for year in range(begin_date.year, end_date.year + 1):
    if year == begin_date.year == end_date.year:
        if begin_date.day <= end_date.day:
            months = range(begin_date.month, end_date.month + 1)
        else:
            months = range(begin_date.month, end_date.month)
    elif year == begin_date.year:
        months = range(begin_date.month, 12 + 1)
    elif year == end_date.year:
        months = range(1, end_date.month)
    else:
        months = range(1, 12 + 1)
    for month in months:
        for currency in currency_to_code:
            if currency not in currencies:
                currencies[currency] = []
            print(f"Fetching info for year: {year}, month: {month}, currency: {currency}")
            currency_value = get_currency_value_by_date(datetime(year, month, 1), currency)
            currencies[currency].append(currency_value)
            time.sleep(0.2)
df = pd.DataFrame(currencies, index=get_month_range_day(begin_date.strftime(r"%d/%m/%Y"),
                                                        get_month_count_between_two_dates(begin_date, end_date)))
df.index.name = "date"
df.to_csv("exchange_rate.csv", encoding="utf-8")
print(df)
