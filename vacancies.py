import os
import requests

from dotenv import load_dotenv
from itertools import count


def get_hh_response(lang):
    url = 'https://api.hh.ru/vacancies'
    print(lang)
    for page in count():
        #print(page)
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


def predict_rub_salary_hh(salary):
    if salary.get('currency') != "RUR":
        return None
    low = salary.get('from')
    high = salary.get('to')
    return predict_salary(low, high)
    '''
    if low and high:
        return (low + high) / 2
    if low:
        return low * 1.2
    return high * 0.8
    '''

def get_average_salary(salaries):
    salary_sum = 0
    value = 0
    for salary in salaries:
        if salary:
            salary_sum += salary
            value += 1
    return int(salary_sum/value)


def main():
    languages = ["Python", "Java", "Javascript", "Ruby",
                 "PHP", "C++", "C", "Go"]
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
                         "vacancies_processed":len(vacancies),
                         "average_salary":avg_salary
                         }
    print(vac)


def get_sj_response(token, lang):
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {'X-Api-App-Id': token}
    payload = {'town':4, 'catalogues': 48,
               'keyword': f'Программист {lang}'}
    response = requests.get(url, headers=headers, params=payload)
    return response.json()


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




if __name__ == "__main__":
    #main()
    load_dotenv()
    sj_token = os.environ['SJ_TOKEN']
    response = get_sj_response(sj_token, 'Java')
    vacancies = response.get('objects')
    empty_vacancies = []
    for vacancy in vacancies:
        profession = vacancy.get('profession')
        town = vacancy.get('town').get('title')
        print(vacancy.get('profession'))
        print(town)
        sj_salary = predict_rub_salary_sj(vacancy)
        print(sj_salary)
        if sj_salary == 0:
            empty_vacancies.append(vacancy)
        print()
