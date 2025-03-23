import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import html_decoration as hd
from .product_data import get_product_data
from .process import extract_keywords
from .search import search_multiple_queries


class WildberriesParserBot:
    def __init__(self, token):
        # Инициализация бота
        self.bot = Bot(token=token)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)

        # Регистрация обработчиков
        self._register_handlers()

    def _register_handlers(self):
        # Команды
        self.dp.message.register(self.cmd_start, Command('start'))
        self.dp.message.register(self.cmd_help, Command('help'))
        
        # Ссылки на Wildberries
        self.dp.message.register(
            self.process_wildberries_link, 
            F.text.contains('wildberries.ru')
        )
        
        # Остальные сообщения
        self.dp.message.register(self.process_other_messages)

    async def cmd_start(self, message: types.Message):
        """Обработчик команды /start"""
        await message.answer(
            "Привет! Я бот для анализа товаров на Wildberries. "
            "Отправь мне ссылку на товар, и я определю его ключевые запросы "
            "и текущие позиции в поисковой выдаче.\n\n"
            "Для получения помощи введи /help"
        )

    async def cmd_help(self, message: types.Message):
        """Обработчик команды /help"""
        await message.answer(
            "Как использовать бота:\n\n"
            "1. Отправь мне ссылку на товар Wildberries (например, https://www.wildberries.ru/catalog/12345678/detail.aspx)\n"
            "2. Я проанализирую товар и найду его ключевые запросы\n"
            "3. Затем я проверю позиции товара в поисковой выдаче по этим запросам\n"
            "4. Ты получишь отчет с результатами анализа\n\n"
            "Примечание: анализ может занять некоторое время, особенно если нужно проверить много запросов."
        )

    async def process_wildberries_link(self, message: types.Message):
        """Обработчик ссылок на Wildberries"""
        url = message.text.strip()

        # Проверяем, что URL относится к Wildberries
        if 'wildberries.ru' not in url:
            await message.answer("Это не похоже на ссылку на Wildberries. Пожалуйста, отправьте корректную ссылку.")
            return

        # Отправляем сообщение о начале анализа
        processing_message = await message.answer("Начинаю анализ товара... Это может занять некоторое время.")

        try:
            # Получаем данные о товаре
            await processing_message.edit_text("Получение информации о товаре...")
            # Запускаем функцию в отдельном потоке, чтобы не блокировать бота
            product_data = await asyncio.to_thread(get_product_data, url)

            # Извлекаем ключевые запросы
            await processing_message.edit_text("Определение ключевых запросов...")
            keywords = await asyncio.to_thread(extract_keywords, product_data)

            # Находим позиции товара
            await processing_message.edit_text("Проверка позиций товара в поисковой выдаче... Это может занять несколько минут.")
            positions = await asyncio.to_thread(search_multiple_queries, product_data['id'], keywords)

            # Формируем отчет
            report = self._format_report(product_data, keywords, positions)

            # Отправляем отчет
            await processing_message.delete()
            await message.answer(report, parse_mode="HTML")

        except Exception as e:
            logging.error(f"Ошибка при обработке ссылки: {e}")
            await processing_message.edit_text(f"Произошла ошибка при анализе товара: {str(e)}")

    def _format_report(self, product_data, keywords, positions):
        """Форматирует отчет с результатами анализа"""
        report = f"{hd.bold('Анализ товара:')} {product_data['name']}\n\n"
        report += f"{hd.bold('Бренд:')} {product_data['brand']}\n"
        report += f"{hd.bold('Цена:')} {product_data['price']['current']} ₽\n\n"

        report += f"{hd.bold('Ключевые запросы:')}\n"
        for keyword in keywords:
            report += f"• {keyword}\n"

        report += f"\n{hd.bold('Позиции в поисковой выдаче:')}\n"
        found_count = 0

        for keyword, data in positions.items():
            if 'not_found' in data and data['not_found']:
                report += f"• {hd.italic(keyword)}: не найден в первых {data.get('max_pages', 10)} страницах\n"
            else:
                found_count += 1
                report += f"• {hd.italic(keyword)}: {data['position']} (стр. {data['page']}, поз. {data['position_on_page']})\n"

        # Добавляем статистику
        report += f"\n{hd.bold('Статистика:')}\n"
        report += f"• Запросов проверено: {len(positions)}\n"
        report += f"• Найдено в выдаче: {found_count}\n"

        # Если товар найден хотя бы по одному запросу, вычисляем среднюю позицию
        if found_count > 0:
            total_position = sum(data['position'] for keyword, data in positions.items(
            ) if 'not_found' not in data or not data['not_found'])
            avg_position = total_position / found_count
            report += f"• Средняя позиция: {avg_position:.1f}\n"

        return report

    async def process_other_messages(self, message: types.Message):
        """Обработчик для всех остальных сообщений"""
        await message.answer(
            "Я не понимаю это сообщение. Пожалуйста, отправьте мне ссылку на товар Wildberries "
            "или введите /help для получения помощи."
        )

    async def start(self):
        """Запускает бота"""
        await self.dp.start_polling(self.bot, skip_updates=True)
