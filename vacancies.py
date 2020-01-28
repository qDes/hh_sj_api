import os
import requests

from dotenv import load_dotenv
from itertools import count
from terminaltables import AsciiTable


def print_vacancies_table(title, vacancies):
    table_data = [['Язык программирования', 'Вакансий найдено',
                   'Вакансий обработано', 'Средняя зарплата']]
    for lang, lang_vacancies in vacancies.items():
        table_data.append([lang]+list(lang_vacancies.values()))
    table_instance = AsciiTable(table_data, title)
    table_instance.justify_columns[2] = 'left'
    print(table_instance.table)
    print()


def get_hh_response(lang):
    url = 'https://api.hh.ru/vacancies'
    for page in count():
        payload = {"text": f'Программист {lang}', "areas": "Москва",
                   "only_with_salary": True, "page": page}
        try:
            response = requests.get(url, params=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            break
        page_data = response.json()
        if page >= page_data['pages']:
            break
        yield page_data


def get_sj_response(token, lang):
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {'X-Api-App-Id': token}
    for page in count():
        payload = {"town": 4, "catalogues": 48,
                   "keyword": f"Программист {lang}",
                   "page": page}
        try:
            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            break
        page_data = response.json()
        yield page_data
        if not page_data.get('more'):
            break


def predict_rub_salary_hh(salary):
    if salary.get('currency') != "RUR":
        return None
    low = salary.get('from')
    high = salary.get('to')
    return predict_salary(low, high)


def get_average_salary(salaries):
    salary_sum = 0
    value = 0
    for salary in salaries:
        if salary:
            salary_sum += salary
            value += 1
    if value == 0:
        return None
    return int(salary_sum/value)


def parse_vacancies_hh(languages):
    vac = {}
    for language in languages:
        vacancies = []
        for chunk in get_hh_response(language):
            vacancies += chunk['items']
        value = chunk['found']
        salaries = []
        for vacancy in vacancies:
            salary = vacancy.get('salary')
            salaries.append(predict_rub_salary_hh(salary))
        avg_salary = get_average_salary(salaries)
        vac[language] = {"vacancies_found": value,
                         "vacancies_processed": len(vacancies),
                         "average_salary": avg_salary
                         }
    return vac


def predict_salary(salary_from, salary_to):
    if salary_from == salary_to == 0:
        return None
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from:
        return salary_from * 1.2
    return salary_to * 0.8


def predict_rub_salary_sj(vacancy):
    if vacancy.get('currency') != 'rub':
        return None
    salary_from = vacancy.get('payment_from')
    salary_to = vacancy.get('payment_to')
    return predict_salary(salary_from, salary_to)


def parse_vacancies_sj(languages):
    load_dotenv()
    sj_token = os.environ['SJ_TOKEN']
    vac = {}
    for language in languages:
        vacancies = []
        for chunk in get_sj_response(sj_token, language):
            vacancies += chunk['objects']
        value = chunk.get('total')
        salaries = []
        for vacancy in vacancies:
            salary = predict_rub_salary_sj(vacancy)
            salaries.append(salary)
        avg_salary = get_average_salary(salaries)
        vac[language] = {"vacancies_found": value,
                         "vacancies_processed": len(vacancies),
                         "average_salary": avg_salary
                         }
    return vac


def main():
    languages = ["Python", "Java", "Javascript", "Ruby",
                 "PHP", "C++", "C", "Go"]
    hh_vacancies = parse_vacancies_hh(languages)
    sj_vacancies = parse_vacancies_sj(languages)
    print_vacancies_table("HeadHunter Moscow", hh_vacancies)
    print_vacancies_table("SuperJob Moscow", sj_vacancies)


if __name__ == "__main__":
    main()
