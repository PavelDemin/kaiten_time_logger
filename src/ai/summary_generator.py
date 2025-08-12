from typing import List, Optional

from src.ai.base_llm import BaseLLM
from src.ai.constants import AiProvider
from src.ai.yandex_provider import YandexGPTProvider
from src.core.config import config
from src.utils.logger import logger


class SummaryGenerator:
    """Класс для генерации описаний по коммитам"""

    def __init__(self):
        self._llm_provider: Optional[BaseLLM] = None
        self._initialize_provider()

    def _initialize_provider(self) -> None:
        """Инициализирует провайдера LLM на основе настроек"""
        if not config.ai_enabled:
            self._llm_provider = None
            return

        try:
            if config.ai_provider == AiProvider.yandex:
                if config.ai_api_key and config.ai_folder_id:
                    self._llm_provider = YandexGPTProvider(
                        api_key=config.ai_api_key, folder_id=config.ai_folder_id, model=config.ai_model
                    )
                    logger.info('Yandex GPT провайдер инициализирован')
                else:
                    logger.warning('Не заданы Yandex API ключ или folder_id')
                    self._llm_provider = None
            else:
                logger.warning(f'Неизвестный AI провайдер: {config.ai_provider}')
                self._llm_provider = None

        except Exception as e:
            logger.error(f'Ошибка инициализации AI провайдера: {e}')
            self._llm_provider = None

    @property
    def is_enabled(self) -> bool:
        """Проверяет, включена ли генерация описаний"""
        return config.ai_enabled and self._llm_provider is not None

    @property
    def is_available(self) -> bool:
        """Проверяет доступность LLM провайдера"""
        return self.is_enabled and self._llm_provider.is_available()

    def generate_task_summary(self, commits: List[str]) -> Optional[str]:
        """
        Генерирует описание для задачи на основе коммитов

        Args:
            commits: Список сообщений коммитов

        Returns:
            Сгенерированное описание или None
        """
        if not self.is_enabled:
            logger.debug('Генерация описаний отключена или провайдер не инициализирован')
            return None

        if not commits:
            logger.debug('Список коммитов пуст')
            return None

        filtered_commits = [commit.strip() for commit in commits if commit.strip()]
        if not filtered_commits:
            logger.debug('Все коммиты пустые после фильтрации')
            return None

        try:
            summary = self._llm_provider.generate_summary(commits=filtered_commits, language=config.ai_language)

            if summary:
                logger.info(f'Успешно сгенерировано описание для {len(filtered_commits)} коммитов')
                return summary
            else:
                logger.warning('LLM провайдер вернул пустое описание')
                return None

        except Exception as e:
            logger.error(f'Ошибка при генерации описания: {e}')
            return None

    def reinitialize(self) -> None:
        """Переинициализирует провайдера (например, после изменения настроек)"""
        logger.info('Переинициализация AI провайдера')
        self._initialize_provider()
