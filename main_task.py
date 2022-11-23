import task_table
import task_statistics


class Launcher:
    """Класс для запуска выбранной пользователем программы"""

    def __init__(self):
        """Инициализирует объект класса Launcher и запускает выбранную пользователем программу."""
        self.output_type = input()
        if self.output_type == "Вакансии":
            app = task_table.InputConnect()
        elif self.output_type == "Статистика":
            app = task_statistics.InputConnect()
        else:
            print("Введен неверный тип вывода!")


launcher = Launcher()
