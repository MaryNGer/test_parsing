import json
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

quote_dct: Dict[str, List[Dict[str, str]]] = {"quotes": []}


def get_pages(button: bool) -> None:
    """
    Получает страницы с цитатами, начиная со второй страницы.

    Args:
        button (bool): Флаг, указывающий, есть ли кнопка для следующей страницы.

    Returns:
        None
    """

    url_template = "https://quotes.toscrape.com/page/{}"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }
    count = 2
    while button:
        url_page = url_template.format(count)
        response = requests.get(url_page, headers=headers)
        if response.status_code == 200:
            button = get_quotes(response)
        else:
            print(f"Ошибка при запросе страницы №{count}: {response.status_code}")
            break
        print(f"Страница №{count} готова")
        count += 1


def get_quotes(response: requests.Response) -> bool:
    """
    Обрабатывает ответ на запрос страницы и извлекает данные о цитатах.

    Args:
       response (requests.Response): Ответ на запрос страницы.

    Returns:
       bool: True, если кнопка следующей страницы найдена, иначе False.
    """

    soup = BeautifulSoup(response.text, "lxml")
    next_button = soup.find("li", class_="next")
    quotes = soup.find_all("div", class_="quote")
    for quote in quotes:
        quote_text = quote.find("span", class_="text").text
        author = quote.find("small", class_="author").text
        author_link = quote.find("a", string="(about)")["href"]
        tags = [tag.text for tag in quote.find_all("a", class_="tag")]
        create_quotes_dct(quote_text, author, author_link, tags)
    return next_button is not None


def create_quotes_dct(
    text: str, author: str, author_link: str, tags: List[str]
) -> None:
    """
    Добавляет данные о цитате в глобальный словарь quote_dct.

    Args:
        text (str): Текст цитаты.
        author (str): Автор цитаты.
        author_link (str): Ссылка на автора.
        tags (list): Список тегов, связанных с цитатой.

    Returns:
        None: Функция не возвращает значения.
    """

    quote_dct["quotes"].append(
        {"quote_text": text, "author": author, "author_link": author_link, "tags": tags}
    )


def create_json_quotes() -> None:
    """
    Сохраняет данные о цитатах в JSON-файл.

    Returns:
        None: Функция не возвращает значения.
    """

    with open("quotes.json", "w", encoding="utf-8") as file:
        json.dump(quote_dct, file, ensure_ascii=False, indent=4)


def get_first_page() -> requests.Response:
    """
    Получает первую страницу с цитатами.

    Returns:
        requests.Response: Ответ на запрос первой страницы.
    """

    url = "https://quotes.toscrape.com/"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }
    return requests.get(url, headers=headers)


def main() -> None:
    """
    Основная функция для запуска процесса скрапинга.

    Returns:
        None: Функция не возвращает значения.
    """

    response = get_first_page()
    if response.status_code == 200:
        next_button = get_quotes(response)
        print("Страница №1 готова")
        if next_button:
            get_pages(True)
    else:
        print(f"Ошибка при запросе страницы №1: {response.status_code}")
    create_json_quotes()


if __name__ == "__main__":
    main()
