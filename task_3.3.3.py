import json
import time
from datetime import datetime

import pandas as pd
import requests


class VacancyParser:
    """Класс для представления парсера вакансий.

    Attributes:
        hour_delta (int): (class attribute) Интервал (в часах) для разбиения суток при парсинге
    """

    hour_delta = 4

    @staticmethod
    def get_vacancies_by_date(date: datetime):
        """Возвращает вакансии опубликованные в указанную дату.

        Args:
            date (datetime): Дата, по которой требуется получить вакансии

        Returns:
            vacancies (list): Список вакансий
        """
        vacancies = []
        for hour in range(0, 24, VacancyParser.hour_delta):
            begin_date = datetime(date.year, date.month, date.day, hour=hour)
            if hour + VacancyParser.hour_delta > 23:
                end_date = datetime(date.year, date.month, date.day, hour=hour, minute=59, second=59)
            else:
                end_date = datetime(date.year, date.month, date.day, hour=hour + VacancyParser.hour_delta)
            first_page_info = VacancyParser.get_vacancies_info_by_page(0, begin_date, end_date)
            total_pages_count = first_page_info["pages"]
            vacancies.extend(map(VacancyParser.get_formatted_vacancy, first_page_info["items"]))
            for page in range(1, total_pages_count):
                vacancies.extend(map(VacancyParser.get_formatted_vacancy,
                                     VacancyParser.get_vacancies_info_by_page(page, begin_date, end_date)["items"]))
                time.sleep(0.2)
        return vacancies

    @staticmethod
    def get_vacancies_info_by_page(page: int, begin_date: datetime, end_date: datetime):
        """Возвращает информацию о количестве вакансий на указанной странице, общем количестве вакансий, вакансиях на
        странице, опубликованных между указанными датами.

        Args:
            page (int): Номер страницы, с которой требуется получить информацию
            begin_date (datetime): Нижняя граница даты публикации вакансии
            end_date (datetime): Верхняя граница даты публикации вакансии

        Returns:
            dict: Информация о количестве вакансий на указанной странице, общем количестве вакансий, вакансиях на странице
        """
        begin_date_str = begin_date.strftime("%Y-%m-%dT%H:%M:%S")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")
        params = {"page": page, "per_page": 100, "date_from": begin_date_str, "date_to": end_date_str, "specialization": 1}
        req = requests.get("https://api.hh.ru/vacancies", params)
        req.close()
        data = json.loads(req.content.decode())
        return data

    @staticmethod
    def get_formatted_vacancy(vacancy: dict):
        """Возвращает вакансию только с необходимыми полями на основе переданной вакансии.

        Args:
            vacancy (dict): Вакансия

        Returns:
            dict: Отформатированная вакансия
        """
        new_vacancy = {}
        new_vacancy["name"] = vacancy["name"]
        if vacancy["salary"] is not None:
            new_vacancy["salary_from"] = vacancy["salary"]["from"]
            new_vacancy["salary_to"] = vacancy["salary"]["to"]
            new_vacancy["salary_currency"] = vacancy["salary"]["currency"]
        else:
            new_vacancy["salary_from"] = None
            new_vacancy["salary_to"] = None
            new_vacancy["salary_currency"] = None
        if vacancy["area"] is not None:
            new_vacancy["area_name"] = vacancy["area"]["name"]
        else:
            new_vacancy["area_name"] = None
        new_vacancy["published_at"] = vacancy["published_at"]
        return new_vacancy


class VacancyConverter:
    """Класс для представления конвертера вакансий в csv файл."""

    @staticmethod
    def convert_vacancies_to_csv(vacancies: list, output_csv_filename: str):
        """Сохраняет список вакансий в csv файл.

        Args:
            vacancies (list): Список вакансий
            output_csv_filename (str): Имя файла результата
        """
        df = pd.DataFrame(vacancies)
        df.to_csv(output_csv_filename, index=False, encoding="utf-8")


date_to_parse = datetime(2022, 11, 21)
vacancies = VacancyParser.get_vacancies_by_date(date_to_parse)
VacancyConverter.convert_vacancies_to_csv(vacancies, "vacancies_21_11_2022.csv")
