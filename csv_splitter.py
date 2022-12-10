import pandas as pd


def split_csv_by_year(csv_file_path, new_dir_path, year_key):
    """Разделяет csv файл по годам, сохраняя отдельный csv для каждого года.

    Args:
        csv_file_path (str): Путь до исходного csv файла
        new_dir_path (str): Путь до папки, в которую требуется сохранить результаты
        year_key (str): Название столбца дат
    """
    df = pd.read_csv(csv_file_path)
    for (n), group in df.groupby(df[year_key].map(lambda x: int(x[:4]))):
        group.to_csv(f'{new_dir_path}{n}.csv', index=False)


if __name__ == "__main__":
    split_csv_by_year("./vacancies_by_year.csv", "./splitted_csv/", "published_at")
