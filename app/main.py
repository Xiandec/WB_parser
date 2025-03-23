from .bot import WildberriesParserBot
import os
import logging
import asyncio
from dotenv import load_dotenv
from .healthcheck import start_health_check_server, set_bot_running

# Загружаем переменные окружения из .env файла
load_dotenv()


async def main():
    # Настраиваем логирование
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'wb_bot.log')
    
    # Настраиваем формат логирования
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Настраиваем корневой логгер
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Вывод в консоль
            logging.FileHandler(log_file)  # Вывод в файл
        ]
    )

    # Запускаем сервер для healthcheck
    start_health_check_server()

    # Получаем токен из переменной окружения
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    if not TOKEN:
        logging.error(
            "Не задан токен бота. Установите переменную окружения TELEGRAM_BOT_TOKEN.")
        exit(1)

    # Создаем и запускаем бота
    bot = WildberriesParserBot(TOKEN)

    # Устанавливаем статус работы бота для healthcheck
    set_bot_running(True)

    try:
        logging.info("Бот запущен")
        await bot.start()
    except Exception as e:
        logging.error(f"Ошибка при работе бота: {e}")
        set_bot_running(False)
    finally:
        logging.info("Бот остановлен")
        set_bot_running(False)

if __name__ == '__main__':
    # Запускаем бота
    asyncio.run(main())
