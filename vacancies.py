import requests

def get_vacancies(lang):
    url = 'https://api.hh.ru/vacancies'
    payload = {'text':f'Программист {lang}', "areas":"Москва"}
    response = requests.get(url, params=payload)

    return response.json()


if __name__ == "__main__":
    languages = ["Python", "Java", "Javascript", "Ruby",
                 "PHP", "C++", "C", "Go"]
    vac = {}
    for language in languages:
        resp = get_vacancies(language)
        value = resp.get('found')
        vac[language] = value
    print(vac)
