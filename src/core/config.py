import json
import os
from dataclasses import dataclass
from pathlib import Path

import keyring

from src.ai.constants import AiProvider

KEYRING_SERVICE = 'kaiten_time_logger'
SETTINGS_FILE = Path(os.getenv('APPDATA')) / 'KaitenTimeLogger' / 'settings.json'


@dataclass
class Config:
    kaiten_token: str = ''
    notification_time: str = '18:00'
    git_repo_path: str = ''
    kaiten_url: str = ''  # https://rtsoft-sg.kaiten.ru
    role_id: int = 0  # 6161
    working_time: float = 8.0  # Рабочее время в часах
    ai_enabled: bool = False
    ai_provider: str = AiProvider.yandex
    ai_model: str = 'yandexgpt-lite'
    ai_language: str = 'ru'  # ru, en
    yandex_api_key: str = ''
    yandex_folder_id: str = ''

    def __post_init__(self):
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        stored_token = keyring.get_password(KEYRING_SERVICE, 'kaiten_token')
        if stored_token:
            self.kaiten_token = stored_token

        stored_yandex_key = keyring.get_password(KEYRING_SERVICE, 'yandex_api_key')
        if stored_yandex_key:
            self.yandex_api_key = stored_yandex_key

        if SETTINGS_FILE.exists():
            try:
                settings = json.loads(SETTINGS_FILE.read_text(encoding='utf-8'))
                self.notification_time = settings.get('notification_time', self.notification_time)
                self.git_repo_path = settings.get('git_repo_path', self.git_repo_path)
                self.kaiten_url = settings.get('kaiten_url', self.kaiten_url)
                self.role_id = settings.get('role_id', self.role_id)
                self.working_time = settings.get('working_time', self.working_time)
                self.ai_enabled = settings.get('ai_enabled', self.ai_enabled)
                self.ai_provider = settings.get('ai_provider', self.ai_provider)
                self.ai_model = settings.get('ai_model', self.ai_model)
                self.ai_language = settings.get('ai_language', self.ai_language)
                self.yandex_folder_id = settings.get('yandex_folder_id', self.yandex_folder_id)
            except json.JSONDecodeError:
                pass

    def is_configured(self) -> bool:
        return all(
            [
                self.kaiten_token.strip(),
                self.kaiten_url.strip(),
                self.git_repo_path.strip(),
            ]
        )

    def _save_settings_file(self) -> None:
        settings = {
            'notification_time': self.notification_time,
            'git_repo_path': self.git_repo_path,
            'kaiten_url': self.kaiten_url,
            'role_id': self.role_id,
            'working_time': self.working_time,
            'ai_enabled': self.ai_enabled,
            'ai_provider': self.ai_provider,
            'ai_model': self.ai_model,
            'ai_language': self.ai_language,
            'yandex_folder_id': self.yandex_folder_id,
        }
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding='utf-8')

    @classmethod
    def save_config(
        cls,
        token: str,
        time: str,
        repo_path: str,
        kaiten_url: str,
        role_id: int,
        working_time: float,
        ai_enabled: bool = None,
        yandex_api_key: str = None,
        yandex_folder_id: str = None,
        ai_provider: str = None,
    ) -> None:
        keyring.set_password(KEYRING_SERVICE, 'kaiten_token', token)
        config.kaiten_token = token
        config.notification_time = time
        config.git_repo_path = repo_path
        config.kaiten_url = kaiten_url
        config.role_id = role_id
        config.working_time = working_time

        if ai_provider is not None:
            config.ai_provider = ai_provider
        if ai_enabled is not None:
            config.ai_enabled = ai_enabled
        if yandex_api_key is not None:
            config.yandex_api_key = yandex_api_key
            if yandex_api_key:
                keyring.set_password(KEYRING_SERVICE, 'yandex_api_key', yandex_api_key)
            else:
                try:
                    keyring.delete_password(KEYRING_SERVICE, 'yandex_api_key')
                except keyring.errors.PasswordDeleteError:
                    pass
        if yandex_folder_id is not None:
            config.yandex_folder_id = yandex_folder_id

        config._save_settings_file()


config = Config()
