import time
import random

import requests


def search_wildberries(query, headers=None, max_pages=10):
    """Выполняет поиск на Wildberries по заданному запросу"""
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    encoded_query = requests.utils.quote(query)
    all_products = []

    for page in range(1, max_pages + 1):
        search_url = f"https://search.wb.ru/exactmatch/ru/common/v9/search?ab_testing=false&appType=1&curr=rub&dest=-1257786&lang=ru&page={page}&query={encoded_query}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false"

        # Случайная задержка для имитации человеческого поведения
        time.sleep(random.uniform(1, 3))

        response = requests.get(search_url, headers=headers)
        search_data = response.json()

        if 'data' in search_data and 'products' in search_data['data']:
            products = search_data['data']['products']
            if not products:
                break
            all_products.extend(products)
        else:
            break

    return all_products


def find_product_position(product_id, query, max_pages=10):
    """Находит позицию товара в поисковой выдаче Wildberries"""
    # Ротация User-Agent для имитации разных браузеров
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
    ]
    headers = {'User-Agent': random.choice(user_agents)}

    products = search_wildberries(query, headers, max_pages)

    for index, product in enumerate(products):
        found = False

        # Проверяем разные форматы ID
        if 'id' in product and str(product['id']) == product_id:
            found = True
        if 'nmId' in product and str(product['nmId']) == product_id:
            found = True
        if 'nm' in product and str(product['nm']) == product_id:
            found = True

        if found:
            position = index + 1
            page = (position - 1) // 100 + 1
            position_on_page = ((position - 1) % 100) + 1
            return position, page, position_on_page

    return None, None, None


def search_multiple_queries(product_id, queries, max_pages=10):
    """Находит позиции товара по нескольким запросам"""
    results = {}

    for query in queries:
        # Случайная задержка между запросами
        time.sleep(random.uniform(1, 7))

        position, page, position_on_page = find_product_position(
            product_id, query, max_pages)

        if position is not None:
            results[query] = {
                'position': position,
                'page': page,
                'position_on_page': position_on_page
            }
        else:
            results[query] = {
                'position': None,
                'page': None,
                'position_on_page': None,
                'not_found': True,
                'max_pages': max_pages
            }

    return results
