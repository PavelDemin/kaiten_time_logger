import json
import os
from dataclasses import dataclass
from pathlib import Path

import keyring

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

    def __post_init__(self):
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        stored_token = keyring.get_password(KEYRING_SERVICE, 'kaiten_token')
        if stored_token:
            self.kaiten_token = stored_token
        if SETTINGS_FILE.exists():
            try:
                settings = json.loads(SETTINGS_FILE.read_text(encoding='utf-8'))
                self.notification_time = settings.get('notification_time', self.notification_time)
                self.git_repo_path = settings.get('git_repo_path', self.git_repo_path)
                self.kaiten_url = settings.get('kaiten_url', self.kaiten_url)
                self.role_id = settings.get('role_id', self.role_id)
                self.working_time = settings.get('working_time', self.working_time)
            except json.JSONDecodeError:
                pass

    def _save_settings_file(self) -> None:
        settings = {
            'notification_time': self.notification_time,
            'git_repo_path': self.git_repo_path,
            'kaiten_url': self.kaiten_url,
            'role_id': self.role_id,
            'working_time': self.working_time,
        }
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding='utf-8')

    @classmethod
    def save_config(
        cls, token: str, time: str, repo_path: str, kaiten_url: str, role_id: int, working_time: float
    ) -> None:
        keyring.set_password(KEYRING_SERVICE, 'kaiten_token', token)
        config.kaiten_token = token
        config.notification_time = time
        config.git_repo_path = repo_path
        config.kaiten_url = kaiten_url
        config.role_id = role_id
        config.working_time = working_time
        config._save_settings_file()


config = Config()
