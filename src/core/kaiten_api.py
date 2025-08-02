from datetime import datetime

import requests

from src.utils.logger import logger


class KaitenAPI:
    def __init__(self, token: str, kaiten_url: str, role_id: int):
        self.token = token
        self.base_url = f'{kaiten_url}/api/latest'
        self.role_id = role_id
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
                'role_id': self.role_id,
            }

            response = requests.post(
                f'{self.base_url}/cards/{card_id}/time-logs',
                headers=self.headers,
                json=data,
            )

            return response.status_code == 200

        except requests.RequestException as e:
            logger.error(f'Ошибка сохранения времени в Kaiten: {e}')
            return False

    def get_list_of_user_roles(self) -> list[tuple[id, str]]:
        response = requests.get(
            f'{self.base_url}/user-roles',
            headers=self.headers,
        )
        user_roles = response.json()
        return {role['id']: role['name'] for role in user_roles}
