import csv
import re
import prettytable
import datetime


class Vacancy:

    def __init__(self, name: str, description: str, key_skills: list, experience_id: str, premium: str,
                 employer_name: str, salary: "Salary", area_name: str, published_at: str):
        self.name = name
        self.description = description
        self.key_skills = key_skills
        self.experience_id = experience_id
        self.premium = True if premium == "True" else False
        self.employer_name = employer_name
        self.salary = salary
        self.area_name = area_name
        self.published_at = datetime.datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%S%z")


class Salary:

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

    def __init__(self, salary_from: int, salary_to: int, salary_gross: str, salary_currency: str):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency

    def get_rub_average(self):
        salary_average = (self.salary_from + self.salary_to) / 2
        if self.salary_currency == "RUR":
            return salary_average
        return salary_average * Salary.currency_to_rub[self.salary_currency]


class DataSet:

    def __init__(self, file_name: str):
        self.__file_name = file_name
        self.__list_naming = None

    def get_clear_value(self, value):
        temp = value.split('\n')
        result = [self.get_clear_str(s) for s in temp]
        return '\n'.join(result)

    def get_clear_str(self, s):
        str_without_tags = re.sub("<.*?>", '', s)
        str_without_spaces = ' '.join(str_without_tags.split())
        return str_without_spaces

    def is_empty_file(self):
        return False if self.__list_naming else True

    def csv_reader(self):
        vacancies = open(self.__file_name, 'r', encoding="utf-8-sig")
        self.reader = csv.reader(vacancies)
        self.__list_naming = next(self.reader)

    def csv_filter(self):
        self.vacancies = []
        for line in self.reader:
            if len(line) == len(self.__list_naming) and '' not in line:
                name = self.get_clear_value(line[0])
                description = self.get_clear_value(line[1])
                key_skills = self.get_clear_value(line[2]).split('\n')
                experience_id = self.get_clear_value(line[3])
                premium = self.get_clear_value(line[4])
                employer_name = self.get_clear_value(line[5])
                salary_from = int(float(self.get_clear_value(line[6])))
                salary_to = int(float(self.get_clear_value(line[7])))
                salary_gross = self.get_clear_value(line[8])
                salary_currency = self.get_clear_value(line[9])
                salary = Salary(salary_from, salary_to, salary_gross, salary_currency)
                area_name = self.get_clear_value(line[10])
                published_at = self.get_clear_value(line[11])
                vacancy = Vacancy(name, description, key_skills, experience_id, premium, employer_name, salary,
                                  area_name, published_at)
                salary.rub_average = salary.get_rub_average()
                self.vacancies.append(vacancy)
        self.vacancies_length_before_filtering = len(self.vacancies)

    def formatter(self, filter_key=None, filter_value=None):
        if filter_key and filter_value:
            self.vacancies = list(
                filter(lambda vacancy: self.check_vacancy(vacancy, filter_key, filter_value), self.vacancies))

    def sorter(self, sorting_parameter=None, reverse_sort=False):
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
        if experience == "noExperience":
            return 0
        elif experience == "between1And3":
            return 1
        elif experience == "between3And6":
            return 2
        else:
            return 3

    def check_vacancy(self, vacancy: "Vacancy", filter_key, filter_value):
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


class InputConnect:

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

    def print_vacancies(self, vacancies, vacancy_from, vacancy_to, columns_to_print):
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

    def shorten_string(self, s):
        if len(s) > 100:
            return f"{s[:100]}..."
        return s

    def ask_user(self):
        self.csv_file_name = input("Введите название файла: ")
        # self.csv_file_name = "vacancies_medium.csv"
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

    def check_input(self):
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
        return True

    def __init__(self):
        self.ask_user()
        if self.check_input():
            data_set = DataSet(self.csv_file_name)
            try:
                data_set.csv_reader()
            except StopIteration:
                print("Пустой файл")
            if not data_set.is_empty_file():
                data_set.csv_filter()
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
                    self.print_vacancies(data_set.vacancies, vacancy_from, vacancy_to, self.columns_to_print)

if __name__ == "__main__":
    app = InputConnect()