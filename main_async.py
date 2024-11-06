import asyncio
import json
from typing import Dict, List

import aiohttp
from bs4 import BeautifulSoup

URL = "https://quotes.toscrape.com/page/{}"
quote_dct: Dict[str, List[Dict[str, str]]] = {"quotes": []}


async def create_quotes_dct(quote: BeautifulSoup) -> None:
    """
    Создает словарь с информацией о цитате и добавляет его в глобальный словарь quote_dct.

    Args:
       quote (BeautifulSoup): Объект BeautifulSoup, представляющий блок с цитатой.

    Returns:
       None: Функция не возвращает значения.
    """

    text = quote.find("span", class_="text").text
    author = quote.find("small", class_="author").text
    author_link = quote.find("a", string="(about)")["href"]
    tags = [tag.text for tag in quote.find_all("a", class_="tag")]

    quote_dct["quotes"].append(
        {"quote_text": text, "author": author, "author_link": author_link, "tags": tags}
    )


async def get_quotes(response_text: str) -> None:
    """
    Асинхронно парсит HTML-текст страницы и извлекает информацию о цитатах.

    Args:
        response_text (str): HTML-текст страницы с цитатами.

    Returns:
        None: Функция не возвращает значения.
    """

    soup = BeautifulSoup(response_text, "lxml")
    quotes = soup.find_all("div", class_="quote")
    task_quote = [create_quotes_dct(block) for block in quotes]
    await asyncio.gather(*task_quote)


async def get_pages(client: aiohttp.ClientSession, num: int) -> None:
    """
    Получает HTML-текст страницы с цитатами и вызывает функцию для парсинга цитат.

    Args:
        client (aiohttp.ClientSession): Сессия aiohttp для выполнения HTTP-запросов.
        num (int): Номер страницы для запроса.

    Returns:
        None: Функция не возвращает значения.

    Raises:
        aiohttp.ClientResponseError: Если статус ответа не равен 200.
        aiohttp.ClientConnectionError: Если возникла ошибка подключения.
        aiohttp.ClientPayloadError: Если возникла ошибка при передаче данных.
        asyncio.TimeoutError: Если запрос превысил установленный таймаут.
        aiohttp.ClientConnectorError: Если возникла ошибка подключения к серверу.
        aiohttp.ClientOSError: Если возникла ошибка, связанная с операционной системой.
    """
    url = URL.format(num)
    try:
        async with client.get(url) as response:
            response.raise_for_status()
            print(f"Page #{num} done")
            text = await response.text()
            await get_quotes(text)
    except aiohttp.ClientResponseError as e:
        print(f"Error fetching page #{num}: {e}")
    except aiohttp.ClientConnectionError as e:
        print(f"Connection error fetching page #{num}: {e}")
    except aiohttp.ClientPayloadError as e:
        print(f"Payload error fetching page #{num}: {e}")
    except asyncio.TimeoutError as e:
        print(f"Timeout error fetching page #{num}: {e}")
    except aiohttp.ClientConnectorError as e:
        print(f"Connector error fetching page #{num}: {e}")


async def get_all_pages_quote() -> None:
    """
    Асинхронно получает информацию о цитатах со всех страниц.

    Returns:
        None: Функция не возвращает значения.
    """

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(15)) as client:
        tasks = [get_pages(client, i) for i in range(1, 11)]
        await asyncio.gather(*tasks)


def create_json_quotes() -> None:
    """
    Сохраняет данные о цитатах в JSON-файл.

    Returns:
        None: Функция не возвращает значения.
    """

    with open("quotes_as.json", "w", encoding="utf-8") as file:
        json.dump(quote_dct, file, ensure_ascii=False, indent=4)


def main() -> None:
    """
    Основная функция, которая запускает процесс сбора и сохранения цитат.

    Returns:
        None: Функция не возвращает значения.
    """

    asyncio.run(get_all_pages_quote())
    create_json_quotes()


if __name__ == "__main__":
    main()
