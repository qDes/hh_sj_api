import os
import requests

from dotenv import load_dotenv
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
        yield page_data
        if not page_data.get('more'):
            break


def predict_rub_salary_sj(vacancy):
    if vacancy.get('currency') != 'rub':
        return None
    salary_from = vacancy.get('payment_from')
    salary_to = vacancy.get('payment_to')
    return predict_salary(salary_from, salary_to)


def fetch_vacancies_sj(languages):
    load_dotenv()
    sj_token = os.environ['SJ_TOKEN']
    vacancies_by_lang = {}
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
        vacancies_by_lang[language] = {"vacancies_found": value,
                                       "vacancies_processed": len(vacancies),
                                       "average_salary": avg_salary
                                       }
    return vacancies_by_lang
