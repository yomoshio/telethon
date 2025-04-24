# services/spam_checker.py
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError, PhoneNumberBannedError
import asyncio
import logging
from utils.proxy_pool import get_random_proxy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_spam(session_data):
    try:
        proxy = get_random_proxy()
        logger.info(f"Используется прокси: {proxy}")
        if not proxy:
            logger.warning(f"Прокси не выбран для {session_data['phone']}, пытаюсь без прокси")
            proxy = None

        async with TelegramClient(
            session_data["session_file"],
            session_data["app_id"],
            session_data["app_hash"],
            proxy=None
        ) as client:
            logger.info(f"Подключение к Telegram для {session_data['phone']}")
            await client.connect()

            if not await client.is_user_authorized():
                logger.warning(f"Не авторизован: {session_data['phone']}")
                return "unauthorized"

            logger.info(f"Отправка сообщения @SpamBot для {session_data['phone']}")
            await client.send_message("@SpamBot", "/start")
            await asyncio.sleep(5)

            async for message in client.iter_messages("@SpamBot", limit=1):
                logger.info(f"Ответ от @SpamBot для {session_data['phone']}: {message.message}")
                if "от каких-либо ограничений" in message.message.lower():
                    return "clean"
                else:
                    return "spamban"

    except PhoneNumberBannedError:
        logger.error(f"Номер заблокирован: {session_data['phone']}")
        return "banned"
    except FloodWaitError as e:
        logger.warning(f"Flood wait для {session_data['phone']}: {e.seconds} секунд")
        await asyncio.sleep(e.seconds)
        return await check_spam(session_data)
    except Exception as e:
        logger.error(f"Ошибка для {session_data['phone']}: {e}")
        return "error"