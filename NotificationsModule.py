from AbstractModule import AbstractModule

import ast
import datetime
import json
import os


# Привести дату и время в указанном часовом поясе к UTC
def unify_datetime(user_date, user_time, timezone):
    datetime_utc = datetime.datetime.strptime(user_date + " " + user_time, "%Y-%m-%d %H:%M:%S") -\
                   datetime.timedelta(hours=timezone)

    utc_date_str = str(datetime_utc.date())
    utc_time_str = datetime_utc.time().strftime("%H:%M:%S")

    return {
        "date": utc_date_str,
        "time": utc_time_str
    }


class NotificationsModule(AbstractModule):
    PATH = "./notifications/"

    REQUESTS_QUEUE = []

    def __init__(self):
        super().__init__("notifications_mod")

    def activate(self):
        super(NotificationsModule, self).activate()

    def deactivate(self):
        super(NotificationsModule, self).deactivate()

    # Добавить нотификацию в очередь
    def queue_notification(self, author, timezone, date, time, title, text):
        utc_datetime = unify_datetime(date, time, timezone)

        self.REQUESTS_QUEUE.append({
            "author": author,
            "date": utc_datetime["date"],
            "time": utc_datetime["time"],
            "title": title,
            "text": text
        })

    # Записать очередную нотификацию в файл
    def save_notification(self):
        if len(self.REQUESTS_QUEUE) > 0:
            notification = self.REQUESTS_QUEUE.pop(0)

            if not os.path.exists(self.PATH + notification["date"]):
                with open(self.PATH + notification["date"], "w") as f:
                    f.write("[]")

                f.close()

            with open(self.PATH + notification["date"], "r") as f:
                notifications = list(ast.literal_eval(f.read()))

            f.close()

            notifications.append(notification)

            with open(self.PATH + notification["date"], "w") as f:
                json.dump(notifications, f)

            f.close()

    # Сравнивает текущее время с временами нотификаций сегодняшней даты
    # Если нотификация сработала, она перемещается в историю
    # Возвращает список сработавших нотификаций
    def notify_tick(self):
        notifications_to_send = []

        filename = str(datetime.datetime.utcnow().date())

        if os.path.exists(self.PATH + filename):
            with open(self.PATH + filename, "r") as f:
                notifications = list(ast.literal_eval(f.read()))

            f.close()

            new_notifications = []

            for notification in notifications:
                server_time = datetime.datetime.now(datetime.timezone.utc)
                server_time_str = server_time.strftime("%H:%M:%S")

                if not (filename == notification["date"] and server_time_str >= notification["time"]):
                    new_notifications.append(notification)
                else:
                    notifications_to_send.append(notification)

                    with open(self.PATH + "history", "a") as f:
                        f.write(str(notification) + "\n")

                    f.close()

            with open(self.PATH + filename, "w") as f:
                json.dump(new_notifications, f)

            f.close()

        return notifications_to_send

    # Удалить все файлы с прошедшими датами
    def clear_old(self):
        files = os.listdir(self.PATH)

        for file in files:
            if file != "history" and file <= str(datetime.datetime.utcnow().date()):
                os.remove(self.PATH + file)

    # Очистить историю
    def clear_history(self):
        open(self.PATH + "history", "w").close()

    # Получить всю историю нотификаций
    def get_history(self):
        pass
