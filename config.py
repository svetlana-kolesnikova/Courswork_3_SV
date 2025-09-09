from configparser import ConfigParser
from typing import Dict

def config(filename: str = 'database.ini', section: str = 'postgresql') -> Dict[str, str]:
    """
    Читает параметры подключения к базе данных из файла .ini и возвращает их в виде словаря.

    :param filename: Имя файла конфигурации (по умолчанию 'database.ini')
    :type filename: str
    :param section: Раздел в файле конфигурации (по умолчанию 'postgresql')
    :type section: str
    :return: Словарь с параметрами подключения (ключи и значения - строки)
    :rtype: Dict[str, str]
    :raises Exception: если указанный раздел не найден в файле
    """
    parser = ConfigParser()  # создается парсер
    parser.read(filename)  # загрузка данных из указанного файла .ini
    db: Dict[str, str] = {}  # cоздаётся пустой словарь

    if parser.has_section(section):
        params = parser.items(section)  # сохранение параметров в переменную [(key, value), (key, value)]
        for param in params:
            db[param[0]] = param[1]  # запись параметров из списка кортежей в словарь
    else:
        raise Exception(
            'Selection {0} is not found in the {1} file.'.format(section, filename))
    return db

if __name__ == "__main__":
    print(config(filename='database.ini', section='postgresql'))
