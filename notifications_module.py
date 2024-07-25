import ast
import datetime
import json
import os

import utils

PATH = "./notifications/"

HISTORY = PATH + "/history"


def form_date_and_time(timezone, day, month, year, hours, minutes):
    try:
        target_datetime = datetime.datetime(year, month, day, hours, minutes) - datetime.timedelta(hours=timezone)

        return "ok", target_datetime.date(), target_datetime.time()
    except Exception as e:
        return "error", f"Неверный формат даты и времени:", e


def create_notification(user, date, time, text):
    global PATH

    if not os.path.exists(PATH + str(date)):
        with open(PATH + str(date), "w", encoding="utf-8") as f:
            f.write("[]")

        f.close()

    with open(PATH + str(date), "r", encoding="utf-8") as f:
        notifications = list(ast.literal_eval(f.read()))

    f.close()

    notifications.append({
        "user": str(user),
        "date": str(date),
        "time": str(time),
        "text": text
    })

    with open(PATH + str(date), "w", encoding="utf-8") as f:
        json.dump(notifications, f)

    f.close()


async def check_notifications(client):
    global PATH
    global HISTORY

    utcnow = datetime.datetime.utcnow()

    date = str(utcnow.date())
    time = str(utcnow.time())

    if os.path.exists(PATH + date):
        with open(PATH + date, "r", encoding="utf-8") as f:
            notifications = list(ast.literal_eval(f.read()))

        f.close()

        new_notifications = []

        for notification in notifications:
            if notification["time"] > time:
                new_notifications.append(notification)
            else:
                user = await client.fetch_user(int(notification["user"]))

                await user.send(embed=utils.full_info_embed(
                    "Напоминание",
                    "**" + notification["text"] + "**"
                ))

                with open(HISTORY, "a", encoding="utf-8") as f:
                    f.write(str(notification) + "\n")

                f.close()

        with open(PATH + date, "w", encoding="utf-8") as f:
            json.dump(new_notifications, f)

        f.close()


def clean_files():
    global PATH
    global HISTORY

    date = str(datetime.datetime.utcnow().date())

    for f in os.listdir(PATH):
        if os.path.isfile(os.path.join(PATH, f) and PATH + f != HISTORY):
            if PATH + f < date:
                os.remove(PATH + f)
