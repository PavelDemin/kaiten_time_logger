from datetime import datetime

import requests

from src.utils.logger import logger


class KaitenAPI:
    def __init__(self, token: str, kaiten_url: str):
        self.token = token
        self.base_url = f'{kaiten_url}/api/latest'
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

    def add_time_log(self, card_id: int, time_spent: int, description: str) -> bool:
        try:
            data = {
                'card_id': card_id,
                'time_spent': time_spent,
                'comment': description,
                'for_date': datetime.now().strftime('%Y-%m-%d'),
                'role_id': 6161,
            }

            response = requests.post(
                f'{self.base_url}/cards/{card_id}/time-logs',
                headers=self.headers,
                json=data,
            )

            return response.status_code == 200

        except (ValueError, requests.RequestException) as e:
            logger.error(f'Error adding time log: {e}')
            return False

    def validate_token(self) -> bool:
        try:
            response = requests.get(
                f'{self.base_url}/users/current',
                headers=self.headers,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
