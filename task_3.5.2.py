import csv
import datetime
import sqlite3

import pandas as pd


class CurrencyConverter:
    """Класс для представления конвертера валют.

    Attributes:
        exchange_rate (sqlite3.Connection): Соединение с базой данных курсов валют
        currencies (set): Валюты, присутствующие в базе данных
    """

    def __init__(self, path_to_exchange_rate_db: str):
        """Инициализирует объект CurrencyConverter.

        Args:
            path_to_exchange_rate_db (str): Путь до sqlite файла с курсами валют по месяцам и годам
        """
        self.exchange_rate = sqlite3.connect(path_to_exchange_rate_db)
        cur = self.exchange_rate.cursor()
        self.currencies = set(filter(lambda col: col != "date", map(lambda t: t[0], list(cur.execute("SELECT * FROM EXCHANGE_RATE").description))))
        cur.close()

    def get_rate_at_month_year(self, currency: str, year: int, month: int):
        """Возвращает отношение указанной валюты к рублям в указанный месяц и год.

        Args:
            currency (str): Идентификатор валюты
            year (int): Год
            month (int): Месяц

        Returns:
            float: Отношение указанной валюты к рублям в указанный месяц и год
        """
        if currency not in self.currencies:
            return None
        cur = self.exchange_rate.cursor()
        date_str = f"{year}-{str(month).zfill(2)}"
        sql = f"SELECT {currency} FROM EXCHANGE_RATE WHERE date = '{date_str}'"
        cur.execute(sql)
        rate = cur.fetchone()
        cur.close()
        return rate[0]

    def convert_to_rubles_per_month_year(self, value: float, currency: str, year: int, month: int):
        """Конвертирует указанное количество валюты в рубли по курсу на указанный месяц и год.

        Args:
            value (float): Количество валюты
            currency (str): Идентификатор валюты
            year (int): Год
            month (int): Месяц

        Returns:
            int: Эквивалент указанного количества валюты в рублях
        """
        rate = self.get_rate_at_month_year(currency, year, month)
        if rate is None:
            return None
        return int(value * rate)

    def process_vacancies(self, path_to_vacancies_csv: str, processed_db_filename: str):
        """Обрабатывает csv файл с вакансиями, переводя зарплаты в рубли при необходимости, и сохраняет результат в
        новый sqlite файл.

        Args:
            path_to_vacancies_csv (str): Путь до csv файла с вакансиями
            processed_db_filename (str): Имя файла результата
        """
        vacancies = open(path_to_vacancies_csv, 'r', encoding="utf-8-sig")
        csv_reader = csv.reader(vacancies)
        next(csv_reader)
        data = []
        for line in csv_reader:
            name = line[0]
            salary_from = line[1]
            salary_to = line[2]
            salary_currency = line[3]
            area_name = line[4]
            published_at = datetime.datetime.strptime(line[5], "%Y-%m-%dT%H:%M:%S%z")
            if salary_from == salary_to == "" or salary_currency == "":
                salary = None
            elif (salary_from != "" and salary_to == "") or (salary_from == "" and salary_to != ""):
                if salary_from != "":
                    salary = self.convert_to_rubles_per_month_year(float(salary_from), salary_currency,
                                                                   published_at.year, published_at.month)
                else:
                    salary = self.convert_to_rubles_per_month_year(float(salary_to), salary_currency,
                                                                   published_at.year, published_at.month)
            else:
                mean_salary = (float(salary_from) + float(salary_to)) / 2
                salary = self.convert_to_rubles_per_month_year(mean_salary, salary_currency,
                                                        published_at.year, published_at.month)
            data.append([name, salary, area_name, published_at.strftime("%Y-%m-%dT%H:%M:%S%z")])
        conn = sqlite3.connect(processed_db_filename)
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS vacancies")
        cur.execute("CREATE TABLE vacancies (name, salary, area_name, published_at)")
        cur.executemany("INSERT INTO vacancies VALUES(?, ?, ?, ?)", data)
        conn.commit()
        conn.close()


currency_converter = CurrencyConverter("exchange_rate.sqlite")
currency_converter.process_vacancies("vacancies_dif_currencies.csv", "vacancies.sqlite")
