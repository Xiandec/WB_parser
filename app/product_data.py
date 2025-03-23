import requests
import re
from bs4 import BeautifulSoup


def get_product_data(url):
    """Получает данные о товаре с Wildberries"""
    # Извлекаем ID товара из URL с помощью регулярных выражений
    product_id_match = re.search(r'/catalog/(\d+)/detail\.aspx', url)
    if not product_id_match:
        # Альтернативный формат URL
        product_id_match = re.search(r'/product\?card=(\d+)', url)

    if not product_id_match:
        # Еще один возможный формат
        product_id_match = re.search(r'/detail\.aspx\?.*?article=(\d+)', url)

    if not product_id_match:
        # Новый формат URL Wildberries
        product_id_match = re.search(r'/product/.*?/(\d+)', url)
        
    if not product_id_match:
        raise ValueError(f"Не удалось извлечь ID товара из URL: {url}")

    product_id = product_id_match.group(1)

    # Используем API для получения данных о товаре
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    api_url = f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-1257786&spp=30&ab_testing=false&lang=ru&nm={product_id}"

    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    product_data = response.json()

    # Извлекаем основную информацию о товаре
    product = product_data['data']['products'][0]

    # Получаем цену из первого доступного размера товара
    price_data = {}
    if 'sizes' in product and product['sizes']:
        for size in product['sizes']:
            if 'price' in size:
                price_data = size['price']
                break
    
    price_total = price_data.get('total', 0) / 100 if 'total' in price_data else 0
    price_basic = price_data.get('basic', 0) / 100 if 'basic' in price_data else 0

    result = {
        'id': product_id,
        'name': product.get('name', ''),
        'brand': product.get('brand', ''),
        'price': {
            'current': price_total,
            'original': price_basic
        },
        'description': product.get('description', ''),
    }

    # Дополнительно получаем описание со страницы
    try:
        page_response = requests.get(url, headers=headers)
        soup = BeautifulSoup(page_response.text, 'html.parser')

        description_selectors = [
            'div.collapsable__content p',
            'p.product-params__cell-text',
            'div.product-detail__description',
            'div[data-tag="description"]',
            'div.details-section-content',
            '.product-page__details-section .content-v1'
        ]

        for selector in description_selectors:
            elements = soup.select(selector)
            if elements:
                description = ' '.join(
                    [el.get_text(strip=True) for el in elements])
                if description:
                    result['description'] = description
                    break
    except Exception as e:
        print(f"Ошибка при получении данных страницы: {e}")

    return result
