import cProfile
import csv
import re
import datetime
import sqlite3

import dateutil.tz

import pandas as pd
from prettytable import prettytable


def profile(func):
    def wrapper(*args, **kwargs):
        datafn = func.__name__ + ".oldprofile"
        prof = cProfile.Profile()
        retval = prof.runcall(func, *args, **kwargs)
        prof.dump_stats(datafn)
        return retval

    return wrapper


class Vacancy:
    """Класс для представления вакансии.

    Attributes:
        name (str): Название вакансии
        description (str): Описание вакансии
        key_skills (list): Список навыков, необходимых для вакансии
        experience_id (str): Необходимый опыт работы
        premium (bool): Тип вакансии (премиум или нет)
        employer_name (str): Имя компании
        salary (Salary): Оклад вакансии
        area_name (str): Регион вакансии
        published_at (datetime): Время публикации вакансии
    """

    def __init__(self, name: str, salary: "Salary", area_name: str, published_at: str, description: str = None,
                 key_skills: list = None, experience_id: str = None, premium: str = None,
                 employer_name: str = None):
        """Инициализирует объект Vacancy, выполняет конвертацию для полей premium (в bool) и published_at (в datetime).

        Args:
            name (str): Название вакансии
            salary (Salary): Оклад вакансии
            area_name (str): Регион вакансии
            published_at (str): Время публикации вакансии
            description (str): Описание вакансии
            key_skills (list): Список навыков, необходимых для вакансии
            experience_id (str): Необходимый опыт работы
            premium (str): Тип вакансии (премиум или нет)
            employer_name (str): Имя компании

        >>> Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта").name
        'Программист'
        >>> Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта").description
        'Описание вакансии'
        >>> Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта").key_skills
        ['Python', 'Git']
        >>> Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта").experience_id
        'between1And3'
        >>> Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта").premium
        False
        >>> Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта").employer_name
        'ООО Рога и Копыта'
        >>> Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта").salary.get_rub_average()
        25000.0
        >>> Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта").area_name
        'Екатеринбург'
        >>> Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта").published_at.isoformat()
        '2022-11-23T00:00:00+03:00'
        """
        self.name = name
        self.salary = salary
        self.area_name = area_name
        self.published_at = Vacancy.convert_str_to_datetime_using_string_parsing(published_at)
        self.description = description
        self.key_skills = key_skills
        self.experience_id = experience_id
        self.premium = True if premium == "True" else False
        self.employer_name = employer_name

    # @staticmethod
    # def convert_str_to_datetime_using_strptime(s: str) -> datetime:
    #     return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")

    @staticmethod
    def convert_str_to_datetime_using_string_parsing(s: str) -> datetime:
        year = int(s[:4])
        month = int(s[5:7])
        day = int(s[8:10])
        hour = int(s[11:13])
        minute = int(s[14:16])
        second = int(s[17:19])
        timezone_offset_hours_int = int(s[19:22])
        timezone_delta = datetime.timedelta(hours=timezone_offset_hours_int)
        if timezone_offset_hours_int < 0:
            timezone_delta *= -1
        timezone_offset = dateutil.tz.tzoffset(None, timezone_delta)
        return datetime.datetime(year, month, day, hour, minute, second, tzinfo=timezone_offset)

    # @staticmethod
    # def convert_str_to_datetime_using_dateutil_parser(s: str) -> datetime:
    #     return dateutil.parser.parse(s)


class Salary:
    """Класс для представления зарплаты.

    Attributes:
        currency_to_rub (dict): (class attribute) Словарь для конвертации валют в рубль по курсу
        salary_from (int): Нижняя граница вилки оклада
        salary_to (int): Верхняя граница вилки оклада
        salary_currency (str): Валюта оклада
    """

    currency_to_rub = {
        "AZN": 35.68,
        "BYR": 23.91,
        "EUR": 59.90,
        "GEL": 21.74,
        "KGS": 0.76,
        "KZT": 0.13,
        "RUR": 1,
        "UAH": 1.64,
        "USD": 60.66,
        "UZS": 0.0055,
    }

    def __init__(self, salary_from: int, salary_to: int, salary_currency: str, salary_gross: str = None):
        """Инициализирует объект Salary.

        Args:
            salary_from (int): Нижняя граница вилки оклада
            salary_to (int): Верхняя граница вилки оклада
            salary_currency (str): Валюта оклада
            salary_gross (str): Гросс
        """
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_currency = salary_currency
        self.salary_gross = salary_gross

    def get_rub_average(self):
        """Вычисляет среднюю зарплату из вилки оклада и переводит в рубли, если необходимо.

        Returns:
            float: Средняя зарплата в рублях

        >>> Salary(20000, 20000, "RUR", "Да").get_rub_average()
        20000.0
        >>> Salary(20000.0, 30000, "RUR", "Да").get_rub_average()
        25000.0
        >>> Salary(20000, 30000.0, "RUR", "Да").get_rub_average()
        25000.0
        >>> Salary(3000, 5000, "USD", "Да").get_rub_average()
        242640.0
        """
        salary_average = (self.salary_from + self.salary_to) / 2
        if self.salary_currency == "RUR":
            return salary_average
        return salary_average * Salary.currency_to_rub[self.salary_currency]


class DataSet:
    """Класс для представления данных вакансий.

    Attributes:
        __file_name (str): Имя файла для обработки данных
        __list_naming (list): Названия столбцов таблицы
        reader (_reader): Объект чтения для чтения строк из файла
        vacancies (list): Список вакансий
        vacancies_length_before_filtering (int): Количество вакансий до фильтрации по параметру
        salary_by_year_df (pd.DataFrame): DataFrame средней зарплаты по годам
        vacancies_count_by_year_df (pd.DataFrame): DataFrame количества вакансий по годам
        selected_vacancy_salary_by_year_df (pd.DataFrame): DataFrame средней зарплаты выбранной профессии по годам
        selected_vacancy_count_by_year_df (pd.DataFrame): DataFrame количества выбранной профессии по годам
        salary_by_area_df (pd.DataFrame): DataFrame средней зарплаты по городам
        vacancies_count_by_area_df (pd.DataFrame): DataFrame количества вакансий по городам
        fraction_by_area_df (pd.DataFrame): DataFrame доли вакансий от общего числа вакансий по городам
    """

    def __init__(self, file_name: str):
        """Инициализирует объект DataSet.

        Args:
            file_name (str): Имя файла для обработки данных
        """
        self.__file_name = file_name
        self.__list_naming = None

    @staticmethod
    def get_clear_value(value: str):
        """Разделяет исходную строку по символу переноса строки, после чего очищает каждую отдельную строку от html тегов
        и лишних пробелов и возвращает строку, объединенную символами переноса строки.

        Args:
            value (str): Список строк для очистки

        Returns:
            str: Строка, состоящая из объединненых символами переноса строки строк, очищенных от html тегов и лишних пробелов

        >>> DataSet.get_clear_value("<span>Текст</span>\\n<h1>Заголовок 1   уровня</h1>\\n1   2   3")
        'Текст\\nЗаголовок 1 уровня\\n1 2 3'
        >>> DataSet.get_clear_value("<h1>Без переноса</h1> строк")
        'Без переноса строк'
        >>> DataSet.get_clear_value("Без html-тегов\\nи лишних пробелов")
        'Без html-тегов\\nи лишних пробелов'
        """
        temp = value.split('\n')
        result = [DataSet.get_clear_str(s) for s in temp]
        return '\n'.join(result)

    @staticmethod
    def get_clear_str(s: str):
        """Очищает строку от html тегов и лишних пробелов.

        Args:
            s (str): Строка для очистки

        Returns:
            str: Строка, очищенная от html тегов и лишних пробелов

        >>> DataSet.get_clear_str("<p>Paragraph</p>")
        'Paragraph'
        >>> DataSet.get_clear_str("one two    three   4")
        'one two three 4'
        >>> DataSet.get_clear_str("<div><h1>Заголовок    1 уровня</h1></div>")
        'Заголовок 1 уровня'
        """
        str_without_tags = re.sub("<.*?>", '', s)
        str_without_spaces = ' '.join(str_without_tags.split())
        return str_without_spaces

    def is_empty_file(self):
        """Возвращает True, если файл пуст, либо False, если файл не пуст.

        Returns:
            bool: True или False
        """
        return False if self.__list_naming else True

    def csv_reader(self):
        """Открывает файл для чтения и получает названия столбцов csv файла."""
        vacancies = open(self.__file_name, 'r', encoding="utf-8-sig")
        self.reader = csv.reader(vacancies)
        self.__list_naming = next(self.reader)

    def csv_filter_for_table(self):
        """Считывает вакансии из файла, содержащие все необходимые данные, очищает их от лишних пробелов и html тегов
         и сохраняет их в список вакансий, а также количество вакансий до фильтрации по параметру."""
        self.vacancies = []
        for line in self.reader:
            if len(line) == len(self.__list_naming) and '' not in line:
                name = DataSet.get_clear_value(line[0])
                description = DataSet.get_clear_value(line[1])
                key_skills = DataSet.get_clear_value(line[2]).split('\n')
                experience_id = DataSet.get_clear_value(line[3])
                premium = DataSet.get_clear_value(line[4])
                employer_name = DataSet.get_clear_value(line[5])
                salary_from = int(float(DataSet.get_clear_value(line[6])))
                salary_to = int(float(DataSet.get_clear_value(line[7])))
                salary_gross = DataSet.get_clear_value(line[8])
                salary_currency = DataSet.get_clear_value(line[9])
                salary = Salary(salary_from, salary_to, salary_currency, salary_gross)
                area_name = DataSet.get_clear_value(line[10])
                published_at = DataSet.get_clear_value(line[11])
                vacancy = Vacancy(name, salary, area_name, published_at, description, key_skills, experience_id,
                                  premium, employer_name)
                salary.rub_average = salary.get_rub_average()
                self.vacancies.append(vacancy)
        self.vacancies_length_before_filtering = len(self.vacancies)

    def formatter(self, filter_key=None, filter_value=None):
        """Выполняет фильтрацию списка вакансий, если задан параметр фильтрации и его значение.

        Args:
            filter_key (str): Параметр фильтрации
            filter_value (str): Значение параметра фильтрации
        """
        if filter_key and filter_value:
            self.vacancies = list(
                filter(lambda vacancy: DataSet.check_vacancy(vacancy, filter_key, filter_value), self.vacancies))

    def sorter(self, sorting_parameter=None, reverse_sort=False):
        """Выполняет сортировку списка вакансий, если задан параметр сортировки.

        Args:
            sorting_parameter (str): Параметр сортировки
            reverse_sort (bool): Флаг сортировки в обратном порядке (True, если требуется отсортировать в обратном порядке)
        """
        if sorting_parameter:
            if sorting_parameter == "Название":
                self.vacancies.sort(key=lambda v: v.name, reverse=reverse_sort)
            elif sorting_parameter == "Описание":
                self.vacancies.sort(key=lambda v: v.description, reverse=reverse_sort)
            elif sorting_parameter == "Навыки":
                self.vacancies.sort(key=lambda v: len(v.key_skills), reverse=reverse_sort)
            elif sorting_parameter == "Опыт работы":
                self.vacancies.sort(key=lambda v: self.convert_experience_to_int(v.experience_id), reverse=reverse_sort)
            elif sorting_parameter == "Премиум-вакансия":
                self.vacancies.sort(key=lambda v: v.premium, reverse=reverse_sort)
            elif sorting_parameter == "Компания":
                self.vacancies.sort(key=lambda v: v.employer_name, reverse=reverse_sort)
            elif sorting_parameter == "Оклад":
                self.vacancies.sort(key=lambda v: v.salary.rub_average, reverse=reverse_sort)
            elif sorting_parameter == "Название региона":
                self.vacancies.sort(key=lambda v: v.area_name, reverse=reverse_sort)
            elif sorting_parameter == "Дата публикации вакансии":
                self.vacancies.sort(key=lambda v: v.published_at, reverse=reverse_sort)

    def convert_experience_to_int(self, experience: str):
        """Преобразует требуемый опыт в число, используемое для дальнейшего сравнения.

        Args:
            experience (str): Опыт работы

        Returns:
            int: Опыт работы в виде числа
        """
        if experience == "noExperience":
            return 0
        elif experience == "between1And3":
            return 1
        elif experience == "between3And6":
            return 2
        else:
            return 3

    @staticmethod
    def check_vacancy(vacancy: "Vacancy", filter_key, filter_value):
        """Проверяет вакансию на соответствие значения параметра фильтрации.

        Args:
            vacancy (Vacancy): Вакансия
            filter_key (str): Параметр фильтрации
            filter_value (str): Значение параметра фильтрации

        Returns:
            bool: True, если вакансия соответствует фильтру, иначе False.

        >>> DataSet.check_vacancy(Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта"), "Название", "Аналитик")
        False
        >>> DataSet.check_vacancy(Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта"), "Название", "Программист")
        True
        >>> DataSet.check_vacancy(Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта"), "Опыт работы", "От 1 года до 3 лет")
        True
        >>> DataSet.check_vacancy(Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта"), "Навыки", "Python")
        True
        >>> DataSet.check_vacancy(Vacancy("Программист",Salary(20000, 30000, "RUR", "Да" ),"Екатеринбург","2022-11-23T00:00:00+0300","Описание вакансии",["Python", "Git"],"between1And3","Нет","ООО Рога и Копыта"), "Оклад", 21000)
        True
        """
        if filter_key == "Название":
            return vacancy.name == filter_value
        elif filter_key == "Описание":
            return vacancy.description == filter_value
        elif filter_key == "Опыт работы":
            return InputConnect.experience_naming[vacancy.experience_id] == filter_value
        elif filter_key == "Премиум-вакансия":
            if vacancy.premium:
                return True if filter_value == "Да" else False
            else:
                return True if filter_value == "Нет" else False
        elif filter_key == "Компания":
            return vacancy.employer_name == filter_value
        elif filter_key == "Оклад":
            salary_value = int(filter_value)
            salary_from = float(vacancy.salary.salary_from)
            salary_to = float(vacancy.salary.salary_to)
            if salary_from <= salary_value <= salary_to:
                return True
        elif filter_key == "Навыки":
            filter_skills = filter_value.split(", ")
            if all(filter_skill in vacancy.key_skills for filter_skill in filter_skills):
                return True
        elif filter_key == "Название региона":
            return vacancy.area_name == filter_value
        elif filter_key == "Дата публикации вакансии":
            return vacancy.published_at.strftime("%d.%m.%Y") == filter_value
        elif filter_key == "Идентификатор валюты оклада":
            return InputConnect.currency_naming[vacancy.salary.salary_currency] == filter_value
        return False

    def get_statistics_using_sql(self, path_to_db_file: str, selected_vacancy: str):
        """Производит расчет статистики по требуемой профессии, используя SQL.

        Args:
            path_to_db_file (str): Путь до sqlite файла с вакансиями
            selected_vacancy (str): Профессия, по которой требуется получить статистику
        """
        conn = sqlite3.connect(path_to_db_file)
        salary_by_year_query = pd.read_sql_query("""
        SELECT substr(published_at, 1, 4) AS year,
		round(avg(salary)) AS salary FROM vacancies GROUP BY year;
        """, conn)
        self.salary_by_year_df = pd.DataFrame(salary_by_year_query)
        vacancies_count_by_year_query = pd.read_sql_query("""
        SELECT substr(published_at, 1, 4) AS year,
		count(name) as vacancies_count FROM vacancies GROUP BY year;
        """, conn)
        self.vacancies_count_by_year_df = pd.DataFrame(vacancies_count_by_year_query)
        selected_vacancy_salary_by_year_query = pd.read_sql_query(f"""
        SELECT substr(published_at, 1, 4) AS year,
 		round(avg(salary)) AS selected_vacancy_salary FROM vacancies WHERE name like '%{selected_vacancy}%' GROUP BY year;
        """, conn)
        self.selected_vacancy_salary_by_year_df = pd.DataFrame(selected_vacancy_salary_by_year_query)
        selected_vacancy_count_by_year_query = pd.read_sql_query(f"""
        SELECT substr(published_at, 1, 4) AS year,
        count(name) as selected_vacancy_count FROM vacancies WHERE name like '%{selected_vacancy}%' GROUP BY year;
        """, conn)
        self.selected_vacancy_count_by_year_df = pd.DataFrame(selected_vacancy_count_by_year_query)
        salary_by_area_query = pd.read_sql_query("""
        SELECT area_name, round(avg(salary)) AS salary 
        FROM vacancies 
        GROUP BY area_name 
        HAVING CAST(count(area_name) as REAL) / (SELECT count(area_name) FROM vacancies) >= 0.01
        ORDER BY salary DESC
        LIMIT 10;
        """, conn)
        self.salary_by_area_df = pd.DataFrame(salary_by_area_query)
        fraction_by_area_query = pd.read_sql_query("""
        SELECT area_name, CAST(count(area_name) as REAL) / (SELECT count(area_name) FROM vacancies) AS fraction
        FROM vacancies 
        GROUP BY area_name 
        HAVING fraction >= 0.01
        ORDER BY fraction DESC
        LIMIT 10;
        """, conn)
        self.fraction_by_area_df = pd.DataFrame(fraction_by_area_query)


class InputConnect:
    """Класс для ввода и вывода данных.

    Attributes:
        experience_naming (dict): (class attribute) Словарь для перевода опыта с английского на русский
        salary_gross_naming (dict): (class attribute) Словарь для перевода гросс с английского на русский
        currency_naming (dict): (class attribute) Словарь для перевода идентификатора валюты оклада на русский
        valid_keys (list): (class attribute) Корректные названия параметров для фильтрации и сортировки
        columns (list): (class attribute) Столбцы для вывода таблицы
        file_name (str): Имя csv файла
        filter_parameter (list): Параметр фильтрации и его значение
        sorting_parameter (list): Параметр сортировки и его значение
        is_sorting_parameter_reverse (bool): Флаг сортировки в обратном порядке
        vacancy_range (list): Диапазон вывода
        columns_to_print (list): Требуемые столбцы для вывода таблицы
    """

    experience_naming = {"noExperience": "Нет опыта", "between1And3": "От 1 года до 3 лет",
                         "between3And6": "От 3 до 6 лет", "moreThan6": "Более 6 лет"}
    salary_gross_naming = {"true": "Без вычета налогов", "false": "С вычетом налогов"}
    currency_naming = {"AZN": "Манаты",
                       "BYR": "Белорусские рубли",
                       "EUR": "Евро",
                       "GEL": "Грузинский лари",
                       "KGS": "Киргизский сом",
                       "KZT": "Тенге",
                       "RUR": "Рубли",
                       "UAH": "Гривны",
                       "USD": "Доллары",
                       "UZS": "Узбекский сум"}
    valid_keys = ['Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия',
                  'Компания', 'Нижняя граница вилки оклада', 'Верхняя граница вилки оклада',
                  'Оклад указан до вычета налогов', 'Идентификатор валюты оклада', 'Название региона',
                  'Дата публикации вакансии', 'Оклад']
    columns = ["Название", "Описание", "Навыки", "Опыт работы", "Премиум-вакансия", "Компания", "Оклад",
               "Название региона", "Дата публикации вакансии"]

    def print_vacancies_table(self, vacancies, vacancy_from, vacancy_to, columns_to_print):
        """Печатает таблицу с вакансиями на экран.

        Args:
            vacancies (list): Список вакансий для печати
            vacancy_from (int): Нижняя граница диапазона вывода
            vacancy_to (int): Верхняя граница диапазона вывода
            columns_to_print (list): Требуемые столбцы для вывода таблицы
        """
        table = prettytable.PrettyTable()
        table.field_names = ['№'] + self.columns
        table.max_width = 20
        table.align = 'l'
        table.hrules = prettytable.ALL
        if vacancy_from > 0:
            vacancy_from -= 1
        if vacancy_to != len(vacancies):
            vacancy_to -= 1
        for i in range(len(vacancies)):
            vacancy = vacancies[i]
            result_row = [str(i + 1)]
            result_row.append(self.shorten_string(vacancy.name))
            result_row.append(self.shorten_string(vacancy.description))
            result_row.append(self.shorten_string('\n'.join(vacancy.key_skills)))
            result_row.append(InputConnect.experience_naming[vacancy.experience_id])
            result_row.append("Да" if vacancy.premium else "Нет")
            result_row.append(vacancy.employer_name)
            salary_gross = InputConnect.salary_gross_naming[vacancy.salary.salary_gross.lower()]
            salary_currency = InputConnect.currency_naming[vacancy.salary.salary_currency]
            salary = f"{format(vacancy.salary.salary_from, ',').replace(',', ' ')} - {format(vacancy.salary.salary_to, ',').replace(',', ' ')} ({salary_currency}) ({salary_gross})"
            result_row.append(salary)
            result_row.append(vacancy.area_name)
            result_row.append(vacancy.published_at.strftime("%d.%m.%Y"))
            table.add_row(result_row)
        print(table.get_string(start=vacancy_from, end=vacancy_to, fields=['№'] + list(columns_to_print)))

    def print_statistics(self, data_set: DataSet):
        """Печатает статистику на экран.

        Args:
            data_set (DataSet): Дата-сет статистики
        """
        print(f"Динамика уровня зарплат по годам:\n{data_set.salary_by_year_df.to_string(index=False)}\n")
        print(f"Динамика количества вакансий по годам:\n{data_set.vacancies_count_by_year_df.to_string(index=False)}\n")
        print(f"Динамика уровня зарплат по годам для выбранной профессии:\n"
              f"{data_set.selected_vacancy_salary_by_year_df.to_string(index=False)}\n")
        print(f"Динамика количества вакансий по годам для выбранной профессии:\n"
              f"{data_set.selected_vacancy_count_by_year_df.to_string(index=False)}\n")
        print(
            f"Уровень зарплат по городам (в порядке убывания):\n{data_set.salary_by_area_df.to_string(index=False)}\n")
        print(f"Доля вакансий по городам (в порядке убывания):\n"
              f"{data_set.fraction_by_area_df.to_string(index=False, formatters={'fraction': '{:,.2%}'.format})}\n")

    def shorten_string(self, s):
        """Возвращает укороченную до 100-и символов строку, если её длина превышает 100 символов, иначе исходную строку.

        Args:
            s (str): Строка

        Returns:
            str: Укороченная  или исходная строка
        """
        if len(s) > 100:
            return f"{s[:100]}..."
        return s

    def ask_user(self):
        """Получает необходимые данные ввода от пользователя."""
        self.output_type = input()
        self.file_name = input("Введите название файла: ")
        if self.output_type == "Вакансии":
            self.filter_parameter = input("Введите параметр фильтрации: ").split(": ")
            self.sorting_parameter = input("Введите параметр сортировки: ")
            self.is_sorting_parameter_reverse = input("Обратный порядок сортировки (Да / Нет): ")
            if self.is_sorting_parameter_reverse == "Да":
                self.is_sorting_parameter_reverse = True
            elif self.is_sorting_parameter_reverse == "Нет" or self.is_sorting_parameter_reverse == '':
                self.is_sorting_parameter_reverse = False
            self.vacancy_range = list(map(int, input("Введите диапазон вывода: ").split()))
            self.columns_to_print = input("Введите требуемые столбцы: ").split(', ')
            self.filter_key = self.filter_parameter[0]
        elif self.output_type == "Статистика":
            self.vacancy_name = input("Введите название профессии: ")

    def check_input(self):
        """Проверяет на корректность введенные пользователем данные.

        Returns:
            bool: True, если данные введены корректно, иначе False
        """
        if self.output_type == "Вакансии":
            if len(self.filter_parameter) == 1 and self.filter_key != '':
                print("Формат ввода некорректен")
                return False
            elif self.filter_key not in InputConnect.valid_keys and self.filter_key != '':
                print("Параметр поиска некорректен")
                return False
            elif self.sorting_parameter not in InputConnect.valid_keys and self.sorting_parameter != '':
                print("Параметр сортировки некорректен")
                return False
            elif self.is_sorting_parameter_reverse not in (True, False):
                print("Порядок сортировки задан некорректно")
                return False
            else:
                return True
        elif self.output_type == "Статистика":
            if self.file_name and self.vacancy_name:
                return True
        return False

    def __init__(self):
        """Инициализирует объект класса InputConnect и обрабатывает данные вакансий при корректности введенных
        пользователем данных."""
        self.ask_user()
        if self.check_input():
            data_set = DataSet(self.file_name)
            if self.output_type == "Вакансии":
                try:
                    data_set.csv_reader()
                except StopIteration:
                    print("Пустой файл")
                if not data_set.is_empty_file():
                    data_set.csv_filter_for_table()
                    if len(self.filter_parameter) == 2:
                        filter_key, filter_value = self.filter_parameter
                        if filter_key in InputConnect.valid_keys:
                            data_set.formatter(filter_key, filter_value)
                    if len(self.vacancy_range) == 0:
                        vacancy_from = 0
                        vacancy_to = data_set.vacancies_length_before_filtering
                    elif len(self.vacancy_range) == 1:
                        vacancy_from = self.vacancy_range[0]
                        vacancy_to = data_set.vacancies_length_before_filtering
                    else:
                        vacancy_from, vacancy_to = self.vacancy_range
                    if len(self.columns_to_print) == 1 and self.columns_to_print[0] == '':
                        if len(data_set.vacancies) != 0:
                            self.columns_to_print = self.columns
                        else:
                            self.columns_to_print = []
                    if len(data_set.vacancies) == 0:
                        if data_set.vacancies_length_before_filtering != 0:
                            print("Ничего не найдено")
                        else:
                            print("Нет данных")
                    else:
                        data_set.sorter(self.sorting_parameter, self.is_sorting_parameter_reverse)
                        self.print_vacancies_table(data_set.vacancies, vacancy_from, vacancy_to, self.columns_to_print)
            elif self.output_type == "Статистика":
                data_set.get_statistics_using_sql(self.file_name, self.vacancy_name)
                self.print_statistics(data_set)


if __name__ == "__main__":
    app = InputConnect()
