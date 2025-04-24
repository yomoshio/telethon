# utils/proxy_pool.py
import random
from config import PROXY_LIST
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_random_proxy():
    if not PROXY_LIST:
        logger.warning("Список прокси пуст")
        return None

    try:
        proxy = random.choice(PROXY_LIST)
        host, port, user, password = proxy.split(":")
        logger.info(f"Выбран прокси: {host}:{port}")
        return ("socks5", host, int(port), user, password)
    except ValueError as e:
        logger.error(f"Неверный формат прокси: {proxy}. Ожидается host:port:user:password. Ошибка: {e}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при выборе прокси: {e}")
        return None