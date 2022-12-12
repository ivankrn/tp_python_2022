from datetime import datetime

import numpy as np
import pandas as pd


class CurrencyConverter:
    """Класс для представления конвертера валют.

    Attributes:
        currencies_per_month_year (pd.DataFrame): DataFrame, содержащий курсы валют по месяцам и годам
    """

    def __init__(self, path_to_exchange_rate_csv: str):
        """Инициализирует объект CurrencyConverter.

        Args:
            path_to_exchange_rate_csv (str): Путь до csv файла с курсами валют по месяцам и годам
        """
        self.currencies_per_month_year = pd.read_csv(path_to_exchange_rate_csv, delimiter=',')
        self.currencies_per_month_year["date"] = pd.to_datetime(self.currencies_per_month_year["date"], format="%Y-%m")
        self.currencies_per_month_year = self.currencies_per_month_year.set_index("date")

    def convert_to_rubles_per_month_year(self, value: float, currency: str, year: int, month: int):
        """Конвертирует указанное количество валюты в рубли по курсу на указанный месяц и год.

        Args:
            value (float): Количество валюты
            currency (str): Идентификатор валюты
            year (int): Год
            month (int): Месяц

        Returns:
            float: Эквивалент указанного количества валюты в рублях
        """
        index = datetime(year, month, 1)
        rate = self.currencies_per_month_year.loc[[index]][currency][0]
        return value * rate

    def process_vacancies(self, path_to_vacancies_csv: str, processed_csv_filename: str):
        """Обрабатывает csv файл с вакансиями, переводя зарплаты в рубли при необходимости, и сохраняет результат в
        новый csv файл.

        Args:
            path_to_vacancies_csv (str): Путь до csv файла с вакансиями
            processed_csv_filename (str): Имя файла результата
        """
        df = pd.read_csv(path_to_vacancies_csv, delimiter=',')
        df["published_at"] = pd.to_datetime(df["published_at"], format="%Y-%m-%dT%H:%M:%S%z")
        df["salary"] = df[["salary_from", "salary_to"]].mean(axis=1)
        df["salary"] = df.apply(lambda row: row["salary"] if row["salary_currency"] == "RUR"
        else np.nan if pd.isna(row["salary_currency"])
        else self.convert_to_rubles_per_month_year(row["salary"],
                                                   row["salary_currency"],
                                                   row["published_at"].year, row["published_at"].month),
                                axis=1)
        df.drop(["salary_from", "salary_to", "salary_currency"], axis=1, inplace=True)
        columns = list(df.columns.values)
        columns[1], columns[3] = columns[3], columns[1]
        df = df[columns]
        df.to_csv(processed_csv_filename, encoding="utf-8", index=False)


currency_converter = CurrencyConverter("exchange_rate.csv")
currency_converter.process_vacancies("./splitted_csv/2003.csv", "first_100_vacancies.csv")
