import datetime
import unittest
from task_table import Vacancy, Salary, DataSet


class SalaryTests(unittest.TestCase):
    def test_salary_from(self):
        self.assertEqual(Salary(20000, 25000, "Да", "RUR").salary_from, 20000)

    def test_salary_to(self):
        self.assertEqual(Salary(20000, 25000, "Да", "RUR").salary_to, 25000)

    def test_salary_gross(self):
        self.assertEqual(Salary(20000, 25000, "Да", "RUR").salary_gross, "Да")

    def test_salary_currency(self):
        self.assertEqual(Salary(20000, 25000, "Да", "RUR").salary_currency, "RUR")

    def test_int_get_average(self):
        self.assertEqual(Salary(20000, 25000, "Да", "RUR").get_rub_average(), 22500.0)

    def test_float_get_average(self):
        self.assertEqual(Salary(20000.0, 25000.0, "Да", "RUR").get_rub_average(), 22500.00)

    def test_float_salary_from_in_get_average(self):
        self.assertEqual(Salary(20000.0, 25000, "Да", "RUR").get_rub_average(), 22500)

    def test_float_salary_to_in_get_average(self):
        self.assertEqual(Salary(20000, 25000.0, "Да", "RUR").get_rub_average(), 22500)

    def test_currency_in_get_average(self):
        self.assertEqual(Salary(6000.0, 7500, "Да", "USD").get_rub_average(), 409455)


class VacancyTests(unittest.TestCase):
    def test_vacancy_name(self):
        self.assertEqual(Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                                 "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                                 "2022-11-23T00:00:00+0300").name, "Аналитик")

    def test_vacancy_description(self):
        self.assertEqual(Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                                 "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                                 "2022-11-23T00:00:00+0300").description, "Описание вакансии")

    def test_vacancy_key_skills(self):
        self.assertEqual(Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                                 "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                                 "2022-11-23T00:00:00+0300").key_skills, ["Excel", "Jira", "Zoom"])

    def test_vacancy_experience_id(self):
        self.assertEqual(Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                                 "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                                 "2022-11-23T00:00:00+0300").experience_id, "between1And3")

    def test_vacancy_premium_convertation(self):
        self.assertEqual(Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                                 "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                                 "2022-11-23T00:00:00+0300").premium, False)

    def test_vacancy_employer_name(self):
        self.assertEqual(Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                                 "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                                 "2022-11-23T00:00:00+0300").employer_name, "CoolCompany")

    def test_vacancy_salary_average(self):
        self.assertEqual(Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                                 "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                                 "2022-11-23T00:00:00+0300").salary.get_rub_average(), 104825)

    def test_vacancy_area_name(self):
        self.assertEqual(Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                                 "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                                 "2022-11-23T00:00:00+0300").area_name, "Екатеринбург")

    def test_vacancy_published_at_convertation(self):
        self.assertEqual(Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                                 "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                                 "2022-11-23T00:00:00+0300").published_at, datetime.datetime(2022, 11, 23, 0, 0,
                                                                                             tzinfo=datetime.timezone(
                                                                                                 datetime.timedelta(
                                                                                                     seconds=10800))))


class DataSetTests(unittest.TestCase):
    def test_get_clear_string_html_tags(self):
        self.assertEqual(DataSet.get_clear_str("<p>Paragraph</p>"), 'Paragraph')

    def test_get_clear_string_spaces(self):
        self.assertEqual(DataSet.get_clear_str("one two    three   4"), 'one two three 4')

    def test_get_clear_string_mixed(self):
        self.assertEqual(DataSet.get_clear_str("<div><h1>Заголовок    1 уровня</h1></div>"), 'Заголовок 1 уровня')

    def test_get_clear_string_same(self):
        self.assertEqual(DataSet.get_clear_str("Без лишних пробелов и html тегов"), "Без лишних пробелов и html тегов")

    def test_get_clear_value_mixed(self):
        self.assertEqual(DataSet.get_clear_value("<span>Текст</span>\\n<h1>Заголовок 1   уровня</h1>\\n1   2   3"),
                         'Текст\\nЗаголовок 1 уровня\\n1 2 3')

    def test_get_clear_value_without_breaklines(self):
        self.assertEqual(DataSet.get_clear_value("<h1>Без переноса</h1> строк"),
                         'Без переноса строк')

    def test_get_clear_value_with_only_breaklines(self):
        self.assertEqual(DataSet.get_clear_value("Без html-тегов\\nи лишних пробелов"),
                         'Без html-тегов\\nи лишних пробелов')

    def test_check_vacancy_name(self):
        self.assertEqual(DataSet.check_vacancy(
            Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                    "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                    "2022-11-23T00:00:00+0300"), "Название", "Аналитик"), True)

    def test_check_vacancy_description(self):
        self.assertEqual(DataSet.check_vacancy(
            Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                    "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                    "2022-11-23T00:00:00+0300"), "Описание", "Описание вакансии"), True)

    def test_check_vacancy_one_matching_key_skill(self):
        self.assertEqual(DataSet.check_vacancy(
            Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                    "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                    "2022-11-23T00:00:00+0300"), "Навыки", "Jira"), True)

    def test_check_vacancy_all_matching_key_skills(self):
        self.assertEqual(DataSet.check_vacancy(
            Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                    "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                    "2022-11-23T00:00:00+0300"), "Навыки", "Excel, Jira, Zoom"), True)

    def test_check_vacancy_not_matching_key_skill(self):
        self.assertEqual(DataSet.check_vacancy(
            Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                    "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                    "2022-11-23T00:00:00+0300"), "Навыки", "Git"), False)

    def test_check_vacancy_salary_in_euros(self):
        self.assertEqual(DataSet.check_vacancy(
            Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                    "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                    "2022-11-23T00:00:00+0300"), "Оклад", "1500"), True)

    def test_check_vacancy_currency(self):
        self.assertEqual(DataSet.check_vacancy(
            Vacancy("Аналитик", "Описание вакансии", ["Excel", "Jira", "Zoom"], "between1And3", "Нет",
                    "CoolCompany", Salary(1500, 2000, "Нет", "EUR"), "Екатеринбург",
                    "2022-11-23T00:00:00+0300"), "Идентификатор валюты оклада", "Евро"), True)




if __name__ == '__main__':
    unittest.main()
