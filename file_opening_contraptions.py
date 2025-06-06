import os

from aiogram.exceptions import TelegramBadRequest
from aiogram import Router
from pathlib import Path

from hashing import get_photo_hash

router = Router()

from aiogram.types import InputMediaPhoto, FSInputFile
from typing import Optional, List


def build_file_path(base_dir: str, subdir: str, filename: str) -> Path:
    """
    Собирает путь к файлу из компонентов

    :param base_dir: Базовая директория (например, 'data/images')
    :param subdir: Поддиректория (например, 'products')
    :param filename: Имя файла с расширением (например, 'photo1.jpg')
    :return: Объект Path полного пути
    """
    return Path(base_dir) / subdir / filename



def create_photo_media_group(
        file_paths: List[str],
        captions: Optional[List[str]] = None
) -> List[InputMediaPhoto]:
    """
    Создает медиа-группу из 3 фотографий для отправки через aiogram

    :param file_paths: Список из 3 путей к файлам изображений
    :param captions: Опциональные подписи для каждого фото
    :return: Готовый список InputMediaPhoto объектов
    """

    media_group = []
    for i, path in enumerate(file_paths):
        caption = captions[i] if captions and i < len(captions) else None

        media_group.append(
            InputMediaPhoto(
                media=FSInputFile(os.path.join('user_photos', path)),
                caption=caption
            )
        )

    return media_group

def get_folders(user_dir):
    return [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d))]

async def save_photo(msg, folder_path: str):
    os.makedirs(folder_path, exist_ok=True)
    # Берём фото максимального качества
    photo = msg.photo[-1]

        # Получаем информацию о файле
    file = await msg.bot.get_file(photo.file_id)

        # Проверяем полученный file_path
    if not file.file_path:
            await msg.answer("Ошибка: неверный идентификатор файла.")
            return

        # Проверяем расширение файла
    ext = os.path.splitext(file.file_path)[1].lower()
    if ext not in {'.jpg', '.jpeg', '.png'}:  # Явное указание разрешённых расширений
        await msg.answer("Разрешены только JPG/PNG изображения.")
        return

        # Генерируем уникальное имя файла
    file_name = f"{get_photo_hash(str(photo.file_id))}{ext}"
    dest = os.path.join(folder_path, file_name)

        # Скачивание с обработкой ошибок
    try:
        await msg.bot.download_file(file.file_path, destination=dest)
    except TelegramBadRequest as e:
        await msg.answer(f"Ошибка Telegram: {e.message}")
        return
    except Exception as e:
        await msg.answer(f"Ошибка скачивания: {str(e)}")
        return

    await msg.answer("✅ Фото успешно загружено!")
