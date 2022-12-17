import csv
import datetime

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
        exchange_rate = open(path_to_exchange_rate_csv, 'r', encoding="utf-8-sig")
        csv_reader = csv.reader(exchange_rate)
        currencies = next(csv_reader)[1:]
        self.currencies_per_month_year = {}
        for line in csv_reader:
            date = line[0]
            self.currencies_per_month_year[date] = {}
            for i in range(len(currencies)):
                self.currencies_per_month_year[date][currencies[i]] = float(line[i + 1])

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
        date = f"{year}-{str(month).zfill(2)}"
        rate = self.currencies_per_month_year[date][currency]
        return int(value * rate)

    def process_vacancies(self, path_to_vacancies_csv: str, processed_csv_filename: str):
        """Обрабатывает csv файл с вакансиями, переводя зарплаты в рубли при необходимости, и сохраняет результат в
        новый csv файл.

        Args:
            path_to_vacancies_csv (str): Путь до csv файла с вакансиями
            processed_csv_filename (str): Имя файла результата
        """
        vacancies = open(path_to_vacancies_csv, 'r', encoding="utf-8-sig")
        csv_reader = csv.reader(vacancies)
        next(csv_reader)
        data = [["name", "salary", "area_name", "published_at"]]
        for line in csv_reader:
            name = line[0]
            salary_from = line[1]
            salary_to = line[2]
            salary_currency = line[3]
            area_name = line[4]
            published_at = datetime.datetime.strptime(line[5], "%Y-%m-%dT%H:%M:%S%z")
            if salary_from == salary_to == "" or salary_currency == "":
                salary = ""
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
            if salary != "":
                salary = f"{salary:.1f}"
            data.append([name, salary, area_name, published_at.strftime("%Y-%m-%dT%H:%M:%S%z")])
        with open(processed_csv_filename, 'w', encoding="utf-8-sig", newline='') as processed_csv:
            csv_writer = csv.writer(processed_csv)
            csv_writer.writerows(data)



currency_converter = CurrencyConverter("exchange_rate.csv")
currency_converter.process_vacancies("./splitted_csv/2003.csv", "first_100_vacancies.csv")
