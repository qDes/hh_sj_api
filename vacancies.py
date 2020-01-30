from dotenv import load_dotenv
from tools import print_vacancies_table
from hh_api import fetch_vacancies_hh
from sj_api import fetch_vacancies_sj


def main():
    load_dotenv()
    languages = ["Python", "Java", "Javascript", "Ruby",
                 "PHP", "C++", "C", "Go"]
    hh_vacancies = fetch_vacancies_hh(languages)
    sj_vacancies = fetch_vacancies_sj(languages)
    print_vacancies_table("HeadHunter Moscow", hh_vacancies)
    print_vacancies_table("SuperJob Moscow", sj_vacancies)


if __name__ == "__main__":
    main()
