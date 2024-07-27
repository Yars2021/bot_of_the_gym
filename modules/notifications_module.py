import datetime


class NotificationsModule:
    @staticmethod
    def form_date_and_time(timezone, day, month, year, hours, minutes):
        try:
            target_datetime = datetime.datetime(year, month, day, hours, minutes) - datetime.timedelta(hours=timezone)

            return "ok", target_datetime.date(), target_datetime.time()
        except Exception as e:
            return "error", f"Неверный формат даты и времени:", e
