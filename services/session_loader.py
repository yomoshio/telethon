# services/session_loader.py
import os
import json
import logging
from typing import List, Dict
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from utils.proxy_pool import get_random_proxy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_sessions_from_folder(folder_path: str) -> List[Dict]:
    sessions = []
    logger.info(f"Поиск JSON-файлов в папке: {folder_path}")


    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".json"):
                json_path = os.path.join(root, file)
                session_path = json_path.replace(".json", ".session")
                logger.info(f"Обработка файла: {json_path}")

                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)


                    required_fields = ["phone", "app_id", "app_hash"]
                    if not all(field in data for field in required_fields):
                        logger.error(f"Отсутствуют обязательные поля в {json_path}")
                        continue

                    session_info = {
                        "phone": data["phone"],
                        "app_id": data["app_id"],
                        "app_hash": data["app_hash"],
                        "session_file": session_path
                    }

                    sessions.append(session_info)
                    logger.info(f"Успешно загружена сессия из {json_path}")

                except json.JSONDecodeError as e:
                    logger.error(f"Ошибка декодирования JSON в {json_path}: {e}")
                except Exception as e:
                    logger.error(f"Ошибка чтения {json_path}: {e}")

    if not sessions:
        logger.warning(f"Не найдено валидных JSON-файлов в {folder_path}")
    else:
        logger.info(f"Загружено сессий: {len(sessions)}")

    return sessions