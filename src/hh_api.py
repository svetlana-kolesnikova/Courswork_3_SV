from typing import Any

import requests


class HHParser:
    """
    Парсер для работы с API HeadHunter (https://api.hh.ru/).
    Позволяет получать список работодателей и их вакансии.
    """

    def get_employers(self) -> list[dict[str, Any]]:
        """
        Получает список работодателей с наибольшим количеством открытых вакансий.

        :return: Список словарей с информацией о работодателях.
                 Каждый элемент содержит:
                    - "id" (str): идентификатор работодателя
                    - "name" (str): название работодателя
        :rtype: list[dict[str, Any]]
        :raises requests.exceptions.RequestException: в случае ошибок HTTP-запроса
        """
        url = f"https://api.hh.ru/employers"
        params = {"sort_by": "by_vacancies_open", "per_page": 10}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()["items"]

        employers: list[dict[str, Any]] = []
        for employer in data:
            employers.append({"id": employer["id"], "name": employer["name"]})

        return employers

    def get_vacancies_by_employer_id(self, employer_id: int) -> list[dict[str, Any]]:
        """
        Получает список вакансий работодателя по его ID.

        :param employer_id: Идентификатор работодателя.
        :type employer_id: int
        :return: Список словарей с информацией о вакансиях.
                 Каждый элемент содержит:
                    - "id" (str): идентификатор вакансии
                    - "name" (str): название вакансии
                    - "salary_from" (int): минимальная зарплата (0, если не указана)
                    - "salary_to" (int): максимальная зарплата (0, если не указана)
                    - "url" (str): ссылка на вакансию
        :rtype: list[dict[str, Any]]
        :raises requests.exceptions.RequestException: в случае ошибок HTTP-запроса
        """
        url = f"https://api.hh.ru/vacancies"
        params = {"employer_id": employer_id, "per_page": 50}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()["items"]

        vacancies: list[dict[str, Any]] = []
        for vacancy in data:
            if vacancy["salary"]:
                salary_from = vacancy["salary"]["from"] if vacancy["salary"]["from"] else vacancy["salary"]["to"]
                salary_to = vacancy["salary"]["to"] if vacancy["salary"]["to"] else vacancy["salary"]["from"]
            else:
                salary_from = 0
                salary_to = 0
            vacancies.append(
                {
                    "id": vacancy["id"],
                    "name": vacancy["name"],
                    "salary_from": salary_from,
                    "salary_to": salary_to,
                    "url": vacancy["alternate_url"],
                }
            )
        return vacancies


if __name__ == "__main__":
    hh = HHParser()
    print(hh.get_employers())
    # print(hh.get_vacancies_by_employer_id(1942330))
    # print(hh)
