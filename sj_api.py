import os
import requests

from itertools import count
from tools import get_average_salary, predict_salary


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
        objects = page_data.get('objects')
        yield from objects
        if not page_data.get('more'):
            break


def predict_rub_salary_sj(vacancy):
    if vacancy.get('currency') != 'rub':
        return None
    salary_from = vacancy.get('payment_from')
    salary_to = vacancy.get('payment_to')
    return predict_salary(salary_from, salary_to)


def fetch_vacancies_sj(languages):
    sj_token = os.environ['SJ_TOKEN']
    vacancies_by_lang = {}
    for language in languages:
        vacancies = list(get_sj_response(sj_token, language))
        vacancies_with_salary = 0
        salaries = []
        for vacancy in vacancies:
            salary = predict_rub_salary_sj(vacancy)
            if salary:
                vacancies_with_salary += 1
                salaries.append(salary)
        avg_salary = get_average_salary(salaries)
        vacancies_by_lang[language] = {"vacancies_found": len(vacancies),
                                       "vacancies_processed": vacancies_with_salary,
                                       "average_salary": avg_salary
                                       }
    return vacancies_by_lang
