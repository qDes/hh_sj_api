import requests


def get_hh_response(lang):
    url = 'https://api.hh.ru/vacancies'
    payload = {'text':f'Программист {lang}', "areas":"Москва",
               "only_with_salary": True}
    response = requests.get(url, params=payload)

    return response.json()


def predict_rub_salary(salary):
    if salary.get('currency') != "RUR":
        return None
    low = salary.get('from')
    high = salary.get('to')
    if low and high:
        return (low + high) / 2
    if low:
        return low * 1.2
    return high * 0.8


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
        response = get_hh_response(language)
        value = response.get('found')
        vacancies = response.get('items')
        salaries = []
        for vacancy in vacancies:
            salary = vacancy.get('salary')
            salaries.append(predict_rub_salary(salary))
        avg_salary = get_average_salary(salaries)
        vac[language] = {"vacancies_found": value,
                         "vacancies_processed":len(vacancies),
                         "average_salary":avg_salary
                         }
    print(vac)


if __name__ == "__main__":
    main()
