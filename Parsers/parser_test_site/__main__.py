"""Данный скрипт обеспечивает парсинг "тестового" сайта "calorizator.ru".

ТУТ ПЕРЕЧИСЛЕНО ТО, ЧТО ОН МОЖЕТ ПАРСИТЬ.

:requests.get: Для запроса с сервера.
:os.path: Для указания пути к файлу html.
:json.dump: Для сохранения в JSON-файл.
:csv: Для сохранения в CSV-файл.
:bs4.BeautifulSoup: Для парсинга сайта.

"""
from os import path
from json import dump
import csv

from requests import get
from bs4 import BeautifulSoup

# КОНСТАНТЫ
HEADERS_DICT = {'Accept': '*/*',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
URL = 'https://calorizator.ru/product'
# Символы, которые следует заменить в CSV-, JSON-файлах
UNACCEPTABLE_CHAR_TUPLE = (':', '\'', ' ', '-', ';')

response = get(URL, headers=HEADERS_DICT)
# Запись пути через модуль, чтобы обеспечить кроссплатформенность
source_path = path.join("index.html")


def main():
    """Главная функция."""
    # Сохраняем html страницу на локальном диске, чтобы избежать анти-парсинг системы.
    # Я чуть-чуть тут поменял.
    # if path(source_path).exists():
    with open(source_path, 'w', encoding='utf-8') as source_file:
        source_file.write(response.text)
    # else:
    # Чтение источника
    with open(source_path, 'r', encoding='utf-8') as source_file:
        source = source_file.read()

    soup = BeautifulSoup(source, 'lxml')
    all_categories = soup.find_all('ul', class_="product")[:-1]

    all_categories_dict = add_categories_dict(all_categories)
    write_json(all_categories_dict, "all_categories_dict")
    create_files(all_categories_dict)


def add_categories_dict(all_categories):
    """
    Функция для добавления каждой категории в словарь с её ссылкой.

    :all_categories_dict: Словарь с категориями. Название: ссылка.
    :return: Заполненный словарь.

    """
    all_categories_dict = {}

    # Делаем перебор в каждом блоке таблицы по категориям
    for category in all_categories:
        for item in category.find_all('a'):
            item_text = item.text
            item_href = "https://calorizator.ru/" + item.get('href')
            all_categories_dict[item_text] = item_href

    return all_categories_dict


def write_json(dictionary, name="dict"):
    """Функция, сохраняющая словарь в JSON-формате."""
    way = name + ".json"
    with open(way, 'w', encoding='utf-8') as json_file:
        dump(dictionary, json_file, indent=4, ensure_ascii=False)


def replace_char(name):
    """Функция, заменяющая символы из строки, на '_',
    если они находятся в кортеже недопустимых знаков.

    :UNACCEPTABLE_CHAR_TUPLE: Кортеж недопустимых символов.
    :return: Корректная строка.

    """
    for char in UNACCEPTABLE_CHAR_TUPLE:
        if char in name:
            name = name.replace(char, '_')

    return name


def create_files(dictionary):
    """Функция для создания спарсенных файлов.

    """
    page = 0
    for name, href in dictionary.items():
        if page == 0:
            req = get(url=href, headers=HEADERS_DICT)
            source = req.text
            correct_name = replace_char(name)

            with open(f"data/{page}_{correct_name}.html", 'w', encoding='utf-8') as file_category:
                file_category.write(source)

            with open(f"data/{page}_{correct_name}.html", 'r', encoding='utf-8') as file_category:
                source = file_category.read()

            soup = BeautifulSoup(source, 'lxml')
            head_table = soup.find(class_="views-table sticky-enabled cols-6") \
                .find('thead').find('tr').find_all('th')

            product = head_table[1].text.split(',')[0].strip()
            protein = head_table[2].text.split(',')[0].strip()
            fat = head_table[3].text.split(',')[0].strip()
            carbohydrate = head_table[4].text.split(',')[0].strip()
            kcal = head_table[5].text.split(',')[0].strip()

            with open(f"data/{page}_{correct_name}.csv", 'w', encoding='utf-8-sig', newline='') as file_category:
                writer = csv.writer(file_category, delimiter=';')
                writer.writerow(
                    (product, protein, fat, carbohydrate, kcal)
                )
                pass

            page += 1


if __name__ == "__main__":
    main()
