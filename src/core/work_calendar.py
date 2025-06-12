from datetime import date, datetime
from typing import Optional

import holidays


class WorkCalendar:
    def __init__(self):
        self.calendar = holidays.country_holidays('Russia')

    def is_working_day(self, date_to_check: Optional[date] = None) -> bool:
        date_to_check = date_to_check or date.today()
        return self.calendar.is_working_day(date_to_check)

    def should_show_notification(self, notification_time: str) -> bool:
        if not self.is_working_day():
            return False

        try:
            target_hour, target_minute = map(int, notification_time.split(':'))
            current_time = datetime.now().time()
            return current_time.hour == target_hour and  current_time.minute == target_minute

        except ValueError:
            return False
