import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import string

# Загрузка необходимых ресурсов NLTK
nltk.download('punkt_tab')
nltk.download('stopwords')


def extract_keywords(product_data, num_keywords=5):
    """Извлекает ключевые запросы из данных о товаре"""
    # Объединяем название и описание для анализа
    text = product_data.get('name', '') + ' ' + \
        product_data.get('description', '')
    text = text.lower()

    # Токенизация и удаление стоп-слов
    tokens = word_tokenize(text, language='russian')
    russian_stopwords = set(stopwords.words('russian'))
    tokens = [
        word for word in tokens if word not in russian_stopwords and word not in string.punctuation]

    # Подсчет частоты слов
    word_freq = Counter(tokens)
    common_words = [word for word,
                    _ in word_freq.most_common(20) if len(word) > 3]

    # Формирование ключевых запросов
    keywords = []

    # Бренд + категория товара
    brand = product_data.get('brand', '').lower()
    if brand and len(brand) > 1:
        product_name = product_data.get('name', '').lower()
        if product_name:
            category = product_name.split()[-1]
            if category and len(category) > 3:
                keywords.append(f"{brand} {category}")

    # Первое слово названия + частые слова
    product_name_words = product_data.get('name', '').lower().split()
    if product_name_words:
        first_word = product_name_words[0]
        for word in common_words[:5]:
            if word != first_word and len(word) > 3:
                keywords.append(f"{first_word} {word}")

    # Добавляем комбинации частых слов
    for i in range(min(5, len(common_words))):
        for j in range(i+1, min(10, len(common_words))):
            if len(keywords) >= num_keywords:
                break
            keyword = f"{common_words[i]} {common_words[j]}"
            if keyword not in keywords:
                keywords.append(keyword)

    return keywords[:num_keywords]
