import task_table
import task_statistics


class Launcher:

    very_important_var = 42

    def __init__(self):
        self.output_type = input()
        if self.output_type == "Вакансии":
            app = task_table.InputConnect()
        elif self.output_type == "Статистика":
            app = task_statistics.InputConnect()
        else:
            print("Введен неверный тип вывода!")


launcher = Launcher()
