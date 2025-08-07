import os
import sys
from pathlib import Path

from PIL import Image

from utils.logger import logger


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)


def safe_get_icon(icon_path: Path, size: int | tuple[int, int] = (10, 10)):
    if isinstance(size, int):
        size = (size, size)

    try:
        image = Image.open(icon_path)
        image.thumbnail(size)
        return image
    except Exception as e:
        logger.warning(f'Не удалось загрузить иконку: {e}')
        return Image.new('RGB', size=size, color='blue')
