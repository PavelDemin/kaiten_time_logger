from abc import ABC, abstractmethod
from typing import List, Optional


class BaseLLM(ABC):
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model or self.get_default_model()

    @abstractmethod
    def get_default_model(self) -> str:
        """Возвращает модель по умолчанию для провайдера"""
        pass

    @abstractmethod
    def generate_summary(self, commits: List[str], language: str = 'ru') -> Optional[str]:
        """
        Генерирует описание на основе списка коммитов

        Args:
            commits: Список сообщений коммитов
            language: Язык генерации ('ru' или 'en')

        Returns:
            Сгенерированное описание или None в случае ошибки
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Проверяет доступность LLM"""
        pass

    @staticmethod
    def create_prompt(commits: List[str], language: str = 'ru') -> str:
        commits_text = '\n'.join(f'- {commit}' for commit in commits)

        if language == 'ru':
            return (
                f'Проанализируй коммиты в по задаче и создай краткое описание проделанной работы '
                f'(не более 2-3 предложений). В коммитах могут быть временные метки, идентификаторы задачи и другая '
                f'косвенная информация, игнорируй эти метки при составлении описания: '
                f'Коммиты: {commits_text}'
            )
        else:
            return (
                f'Analyze the task commits and create a brief description of the work done (2-3 sentences): '
                f'Commits: {commits_text}'
            )
