from typing import Any, Dict, List

import psycopg2
from psycopg2 import sql

from config import config
from src.hh_api import HHParser


def create_database(db_name: str) -> None:
    """
    Создает базу данных с указанным именем.
    Если база данных уже существует, она будет удалена и создана заново.

    :param db_name: Название базы данных
    :type db_name: str
    :return: None
    """
    params: Dict[str, Any] = config()
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name)))
    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))

    cur.close()
    conn.close()


def create_tables(db_name: str) -> None:
    """
    Создает таблицы employers и vacancies в указанной базе данных.

    Таблицы:
        - employers: содержит employer_id и name
        - vacancies: содержит vacancy_id, hh_id, employer_id, title, salary_from, salary_to, url

    :param db_name: Название базы данных
    :type db_name: str
    :return: None
    """
    params: Dict[str, Any] = config()
    with psycopg2.connect(dbname=db_name, **params) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE employers (
                    employer_id VARCHAR(32) PRIMARY KEY,
                    name varchar(255) NOT NULL
                )
            """
            )

            cur.execute(
                """
                    CREATE TABLE vacancies (
                        vacancy_id integer PRIMARY KEY,
                        hh_id VARCHAR(32) UNIQUE,
                        employer_id VARCHAR(32) REFERENCES employers(employer_id) ON DELETE CASCADE,
                        title TEXT,
                        salary_from INTEGER,
                        salary_to INTEGER,
                        url TEXT
                    );
                """
            )
    conn.close()


def insert_employers(db_name: str) -> None:
    """
    Получает список работодателей через HHParser и вставляет их в таблицу employers.

    :param db_name: Название базы данных
    :type db_name: str
    :return: None
    """
    hh_parser = HHParser()
    employers: List[Dict[str, Any]] = hh_parser.get_employers()
    params: Dict[str, Any] = config()

    with psycopg2.connect(dbname=db_name, **params) as conn:
        with conn.cursor() as cur:
            for employer in employers:
                cur.execute("INSERT INTO employers VALUES (%s, %s)", (employer["id"], employer["name"]))

    conn.close()


def insert_vacancies(db_name: str) -> None:
    """
    Получает вакансии всех работодателей из таблицы employers через HHParser
    и вставляет их в таблицу vacancies.

    :param db_name: Название базы данных
    :type db_name: str
    :return: None
    """
    hh_parser = HHParser()
    params: Dict[str, Any] = config()

    with psycopg2.connect(dbname=db_name, **params) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT employer_id FROM employers")
            employers = cur.fetchall()

            for (employer_id,) in employers:
                vacancies: List[Dict[str, Any]] = hh_parser.get_vacancies_by_employer_id(employer_id)
                for vacancy in vacancies:
                    cur.execute(
                        """
                        INSERT INTO vacancies (vacancy_id, hh_id, employer_id, title, salary_from, salary_to, url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (vacancy_id) DO NOTHING
                    """,
                        (
                            vacancy["id"],
                            vacancy["id"],  # hh_id = vacancy_id из API
                            employer_id,
                            vacancy["name"],
                            vacancy["salary_from"],
                            vacancy["salary_to"],
                            vacancy["url"],
                        ),
                    )
    conn.close()
