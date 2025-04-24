# services/extractor.py
import os
import tempfile
import logging
import patoolib
from typing import Optional


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_rar_from_file(file_path: str) -> Optional[str]:
    if not os.path.exists(file_path):
        logger.error(f"Файл {file_path} не существует")
        raise FileNotFoundError(f"Файл {file_path} не существует")


    file_size = os.path.getsize(file_path)
    if file_size < 100:
        logger.error(f"Файл {file_path} слишком маленький: {file_size} байт")
        raise ValueError(f"Файл слишком маленький: {file_size} байт")

    logger.info(f"Обработка файла: {file_path}, размер: {file_size} байт")

    extract_to = tempfile.mkdtemp(prefix="sessions_")
    logger.info(f"Создана временная папка: {extract_to}")

    try:
        logger.info(f"Попытка распаковки с patool: {file_path}")
        patoolib.extract_archive(file_path, outdir=extract_to)
        logger.info(f"Архив успешно распакован в {extract_to}")

        extracted_files = []
        for root, dirs, files in os.walk(extract_to):
            for file in files:
                extracted_files.append(os.path.join(root, file))
        
        if not extracted_files:
            logger.error(f"Папка {extract_to} пуста после распаковки")
            raise ValueError("Архив пустой или не распакован")

        logger.info(f"Найдено файлов: {len(extracted_files)}")
        for file in extracted_files:
            logger.info(f"Извлеченный файл: {file}")

        return extract_to

    except Exception as e:
        logger.error(f"Ошибка при распаковке: {e}")
        raise ValueError(f"Не удалось распаковать архив: {e}")

    finally:
        if os.path.exists(extract_to) and not os.listdir(extract_to):
            logger.warning(f"Папка {extract_to} пуста, удаляю")
            os.rmdir(extract_to)