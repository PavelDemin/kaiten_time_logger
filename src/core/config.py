import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    kaiten_token: str = os.getenv('KAITEN_TOKEN', '')
    notification_time: str = os.getenv('NOTIFICATION_TIME', '18:00')
    git_repo_path: str = os.getenv('GIT_REPO_PATH', str(Path.cwd()))
    kaiten_url: str = os.getenv('KAITEN_URL', 'https://rtsoft-sg.kaiten.ru')

    @classmethod
    def save_config(cls, token: str, time: str, repo_path: str, kaiten_url: str) -> None:
        env_path = Path('.env')
        content = (
            f'KAITEN_TOKEN={token}\nNOTIFICATION_TIME={time}\nGIT_REPO_PATH={repo_path}\nKAITEN_URL={kaiten_url}\n'
        )
        env_path.write_text(content, encoding='utf-8')
        load_dotenv(override=True)


config = Config()
