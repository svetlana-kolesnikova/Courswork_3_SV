import sys

from src.db_manager import DBManager
from src.utils import create_database, create_tables, insert_employers, insert_vacancies

print("Здравствуйте!")
DB_NAME = input("Введите название для базы данных (например hh_project):\n")

# создаём базу и таблицы
create_database(DB_NAME)
create_tables(DB_NAME)

# вставляем работодателей и вакансии
insert_employers(DB_NAME)
insert_vacancies(DB_NAME)

# работа через DBManager
db = DBManager(DB_NAME)

print(
    "Выберите действие от 1 до 5:\n"
    "1. Показать компании и количество вакансий\n"
    "2. Показать все вакансии\n"
    "3. Показать среднюю зарплату\n"
    "4. Показать вакансии с зарплатой выше средней\n"
    "5. Показать вакансии по ключевому слову\n"
)
try:
    user_input_1 = int(input().strip())
except ValueError:
    print("Нужно ввести число 1–5. Перезапустите программу.")
    sys.exit(1)

if user_input_1 == 1:
    print("\n--- Компании и количество вакансий ---")
    for row in db.get_companies_and_vacancies_count():
        print(f"{row[0]}: {row[1]} вакансий")

elif user_input_1 == 2:
    print("\n--- Все вакансии ---")
    for row in db.get_all_vacancies()[:10]:
        print(f"{row[0]}: {row[1]}, зарплата от {row[2]} до {row[3]}, ссылка: {row[4]}")

elif user_input_1 == 3:
    print("\n--- Средняя зарплата ---")
    print(db.get_avg_salary())

elif user_input_1 == 4:
    print("\n--- Вакансии с зарплатой выше средней ---")
    for row in db.get_vacancies_with_higher_salary()[:10]:
        print(f"{row[0]}: {row[1]}, зарплата от {row[2]} до {row[3]}, ссылка: {row[4]}")

elif user_input_1 == 5:
    user_input_2 = input("Введите ключевое слово дя поиска вакансий:\n").strip()

    print(f"\n--- Вакансии по ключевому слову '{user_input_2}' ---")
    for row in db.get_vacancies_with_keyword(user_input_2)[:10]:
        print(row)

else:
    print("Нет такого действия.\n" "До новых встреч!")
    sys.exit()
