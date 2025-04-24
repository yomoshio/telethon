import os
import tempfile
import hashlib
from aiogram import Router, F
from aiogram.types import Message
from services.extractor import extract_rar_from_file
from services.session_loader import load_sessions_from_folder
from services.spam_checker import check_spam

router = Router()

@router.message(F.document)
async def handle_rar(message: Message):
    if not message.document.file_name.endswith(".rar"):
        await message.answer("📁 Пожалуйста, отправь архив с расширением .rar")
        return

    file = await message.bot.get_file(message.document.file_id)
    file_path = file.file_path
    file_size = message.document.file_size

    if file_size < 100:
        await message.answer("❌ Архив слишком маленький или поврежден.")
        return

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".rar") as tmp_file:
            tmp_path = tmp_file.name

        await message.bot.download_file(file_path, tmp_path)

        downloaded_size = os.path.getsize(tmp_path)
        if downloaded_size != file_size:
            await message.answer(f"❌ Файл загружен не полностью (ожидалось {file_size} байт, получено {downloaded_size} байт).")
            return

        with open(tmp_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        print(f"MD5 хеш загруженного файла: {file_hash}")

        try:
            extract_dir = extract_rar_from_file(tmp_path)
        except ValueError as e:
            await message.answer(f"❌ Ошибка при распаковке архива: {e}")
            return
        except Exception as e:
            await message.answer(f"❌ Неизвестная ошибка при распаковке: {e}")
            return

        sessions = load_sessions_from_folder(extract_dir)
        if not sessions:
            await message.answer("❌ Не найдено аккаунтов в архиве.")
            return

        await message.answer(f"👥 Найдено аккаунтов: {len(sessions)}\n🔍 Проверяю...")

        clean, spamban, errors = 0, 0, 0
        for sess in sessions:
            try:
                result = await check_spam(sess)
                if result == "clean":
                    clean += 1
                elif result == "spamban":
                    spamban += 1
                else:
                    errors += 1
            except:
                errors += 1

        await message.answer(f"✅ Без ограничений: {clean}\n🚫 Спамблок: {spamban}\n⚠️ Ошибок: {errors}")

    except Exception as e:
        await message.answer(f"❌ Не удалось загрузить архив: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)