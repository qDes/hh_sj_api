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


def predict_salary(salary_from, salary_to):
    if salary_from == salary_to == 0:
        return None
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from:
        return salary_from * 1.2
    return salary_to * 0.8
