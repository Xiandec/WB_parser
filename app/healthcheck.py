import logging
import uvicorn
from fastapi import FastAPI
import threading
import os

app = FastAPI()
logger = logging.getLogger(__name__)

# Глобальная переменная для отслеживания состояния бота
bot_is_running = False

@app.get("/health")
async def health_check():
    """
    Эндпоинт для проверки работоспособности бота
    Возвращает 200 OK, если бот запущен
    """
    if bot_is_running:
        return {"status": "ok"}
    return {"status": "initializing"}, 503

def start_health_check_server():
    """Запускает сервер для healthcheck"""
    port = int(os.environ.get("HEALTH_CHECK_PORT", 8080))
    host = os.environ.get("HEALTH_CHECK_HOST", "0.0.0.0")
    
    logger.info(f"Запуск healthcheck сервера на {host}:{port}")
    
    # Запускаем в отдельном потоке
    uvicorn_thread = threading.Thread(
        target=uvicorn.run,
        args=(app,),
        kwargs={
            "host": host,
            "port": port,
            "log_level": "warning"
        },
        daemon=True
    )
    uvicorn_thread.start()
    
    logger.info("Healthcheck сервер запущен")
    
def set_bot_running(status: bool = True):
    """Устанавливает статус работы бота"""
    global bot_is_running
    bot_is_running = status 