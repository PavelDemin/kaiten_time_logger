from datetime import datetime

import requests

from ..logger import logger


class KaitenAPI:
    def __init__(self, token: str):
        self.token = token
        self.base_url = 'https://kaiten.ru/api/latest'
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

    def add_time_log(self, card_id: str, time_spent: str, description: str) -> bool:
        try:
            hours, minutes = map(int, time_spent.split('.'))
            total_minutes = hours * 60 + minutes

            data = {
                'cardId': card_id,
                'minutes': total_minutes,
                'description': description,
                'date': datetime.now().strftime('%Y-%m-%d'),
            }

            response = requests.post(
                f'{self.base_url}/cards/time-logs',
                headers=self.headers,
                json=data,
            )

            return response.status_code == 201

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
