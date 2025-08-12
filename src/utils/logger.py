import logging
import sys
from pathlib import Path


def setup_logger(name: str = 'kaiten_logger') -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.propagate = False
        return logger

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    project_root = Path(__file__).resolve().parents[2]
    log_dir = project_root / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_dir / 'kaiten_logger.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger


logger = setup_logger()
