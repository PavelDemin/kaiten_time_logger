from typing import List, Optional

from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk._auth import APIKeyAuth

from src.ai.base_llm import BaseLLM
from src.utils.logger import logger


class YandexGPTProvider(BaseLLM):
    """Провайдер для Yandex GPT"""

    def __init__(self, api_key: str, folder_id: str, model: str = None):
        self.folder_id = folder_id
        self._sdk = YCloudML(folder_id=folder_id, auth=APIKeyAuth(api_key))
        super().__init__(api_key, model)

    def get_default_model(self) -> str:
        return 'yandexgpt-lite'

    def _completions(self):
        """Возвращает объект модели completions для текущей модели."""
        return self._sdk.models.completions(self.model)

    def generate_summary(self, commits: List[str], language: str = 'ru') -> Optional[str]:
        """Генерирует описание с помощью Yandex GPT через SDK"""
        if not commits:
            logger.warning('Список коммитов пуст, описание не может быть сгенерировано')
            return None

        try:
            prompt = self.create_prompt(commits, language)
            messages = [{'role': 'user', 'text': prompt}]

            model = self._completions().configure(temperature=0.3)
            result = model.run(messages)

            summary: Optional[str] = None
            for alternative in result:
                text = getattr(alternative, 'text', None)
                if isinstance(text, str) and text.strip():
                    summary = text.strip()
                    break

            if summary:
                logger.info(f'Успешно сгенерировано описание: {summary[:50]}...')
                return summary

            logger.error('SDK вернул пустой результат без текста')
            return None

        except Exception as e:
            logger.error(f'Ошибка при обращении к Yandex GPT SDK: {e}')
            return None

    def is_available(self) -> bool:
        """Проверяет доступность Yandex GPT через SDK"""
        if not self.api_key or not self.folder_id:
            return False

        try:
            test_messages = 'test messages'
            result = self._completions().configure(temperature=0.1).run(test_messages)
            for alternative in result:
                text = getattr(alternative, 'text', None)
                return isinstance(text, str)
            return False
        except Exception as e:
            logger.debug(f'Yandex GPT недоступен: {e}')
            return False
