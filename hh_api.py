import requests

from itertools import count
from tools import predict_salary
from tools import get_average_salary


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
        items = page_data['items']
        yield from items #page_data


def predict_rub_salary_hh(salary):
    if salary.get('currency') != "RUR":
        return None
    low = salary.get('from')
    high = salary.get('to')
    return predict_salary(low, high)


def fetch_vacancies_hh(languages):
    vacancies_by_lang = {}
    for language in languages:
        vacancies = list(get_hh_response(language))
        vacancies_with_salary = 0
        salaries = []
        for vacancy in vacancies:
            salary_fork = vacancy.get('salary')
            salary = predict_rub_salary_hh(salary_fork)
            if salary:
                vacancies_with_salary += 1
                salaries.append(salary)
        avg_salary = get_average_salary(salaries)
        vacancies_by_lang[language] = {"vacancies_found": len(vacancies),
                                       "vacancies_processed": vacancies_with_salary,
                                       "average_salary": avg_salary
                                       }
    return vacancies_by_lang
