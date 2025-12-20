from typing import Any, List, Optional, Tuple, Dict

import psycopg2

from config import config


class DBManager:
    """
    Класс для работы с базой данных PostgreSQL через psycopg2.
    """

    def __init__(self, db_name: str) -> None:
        """
        Инициализация менеджера БД.
        :param db_name: имя базы данных.
        """
        self.db_name = db_name

    def __execute_query(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[tuple]:
        """
        Выполнение SQL-запроса.
        :param query: SQL-запрос.
        :param params: параметры для подстановки в запрос.
        :return: результат выполнения запроса.
        """
        params_db: Dict[str, str] = config()
        with psycopg2.connect(dbname=self.db_name, **params_db) as conn:
            with conn.cursor() as cur:
                if params:
                    cur.execute(query, params)
                else:
                    cur.execute(query)
                result = cur.fetchall()
        conn.close()
        return result

    def get_companies_and_vacancies_count(self) -> list[tuple]:
        """
        Получает список всех компаний и количество вакансий у каждой.
        :return: список кортежей (название компании, количество вакансий).
        """
        query = """
            SELECT e.name, COUNT(v.vacancy_id)
            FROM employers e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.name
        """
        return self.__execute_query(query)

    def get_all_vacancies(self) -> list[tuple]:
        """
        Получает список всех вакансий с указанием компании, названия, зарплаты и ссылки.
        :return: список кортежей (компания, вакансия, salary_from, salary_to, url).
        """
        query = """
            SELECT e.name AS company_name,
                   v.title AS vacancy_title,
                   v.salary_from,
                   v.salary_to,
                   v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
        """
        return self.__execute_query(query)

    def get_avg_salary(self) -> Optional[float]:
        """
        Получает среднюю зарплату по вакансиям.
        :return: среднее значение зарплаты (округлено до 2 знаков).
        """
        query = """
            SELECT ROUND(AVG((COALESCE(v.salary_from, v.salary_to) + 
                        COALESCE(v.salary_to, v.salary_from)) / 2.0), 2)
            FROM vacancies v
            WHERE v.salary_from IS NOT NULL OR v.salary_to IS NOT NULL
        """
        return self.__execute_query(query)[0][0]

    def get_vacancies_with_higher_salary(self) -> Any:
        """
        Получает список вакансий с зарплатой выше средней.
        :return: список кортежей (компания, вакансия, salary_from, salary_to, url).
        """
        avg_salary = self.get_avg_salary()
        query = """
            SELECT e.name, v.title, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE (COALESCE(v.salary_from, v.salary_to) + 
                   COALESCE(v.salary_to, v.salary_from)) / 2.0 > %s
        """
        return self.__execute_query(query, (avg_salary,))

    def get_vacancies_with_keyword(self, keyword: str) -> Any:
        """
        Получает список вакансий, содержащих ключевое слово в названии.
        :param keyword: слово для поиска (например, 'python').
        :return: список кортежей (компания, вакансия, salary_from, salary_to, url).
        """
        query = """
            SELECT e.name, v.title, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE LOWER(v.title) LIKE LOWER(%s)
        """
        return self.__execute_query(query, (f"%{keyword}%",))
