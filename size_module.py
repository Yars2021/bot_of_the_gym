import ast
import json
import os

from random import randint


FILE = "./.size_table"

MESSAGES = [
    "Волшебная палочка",
    "Козырь в рукаве",
    "Питон в кустах",
    "Мясная сигара",
    "Третья нога",
    "Экскалибур",
    "Авторитет",
    "Морковка",
    "Членохер",
    "Чупачупс",
    "Сюрприз",
    "Хоботок",
    "Прикол",
    "Талант",
    "Ствол",
    "Маяк",
    "Удав"
]


def init():
    global FILE

    if not os.path.exists(FILE):
        with open(FILE, "w", encoding="utf-8") as f:
            f.write("{}")

        f.close()


def get_secret(max_chance):
    if randint(0, 99) < max_chance:
        return "(в жопе) "
    else:
        return ""


def get_length(size):
    if randint(0, 14) == 9:
        return "как " + str(size / 4) + " гориллы"
    else:
        return str(size) + "см"


def get_size(user_id, date):
    global MESSAGES
    global FILE

    with open(FILE, "r", encoding="utf-8") as f:
        stats = ast.literal_eval(f.read())

    f.close()

    call_date = str(date.date())

    if user_id == "429951059650150411":
        stats[user_id] = [call_date, 50, "", 0]
    elif user_id == "318056725070741506":
        stats[user_id] = [call_date, 15.5, "", 0]

    if user_id not in stats:
        stats[user_id] = [call_date, randint(1, 40), get_secret(1), 1]
    elif call_date != stats[user_id][0]:
        chance = stats[user_id][3]
        next_chance = 1

        secret = get_secret(chance)

        if secret == "":
            next_chance = min(chance + 1, 20)

        stats[user_id] = [call_date, randint(1, 40), secret, next_chance]

    with(open(FILE, "w", encoding="utf-8")) as f:
        json.dump(stats, f)

    f.close()

    return MESSAGES[randint(0, len(MESSAGES) - 1)] + " у тебя " + \
        stats[user_id][2] + get_length(stats[user_id][1])


def get_sum(date):
    global FILE

    with open(FILE, "r", encoding="utf-8") as f:
        stats = ast.literal_eval(f.read())

    f.close()

    call_date = str(date.date())

    size_sum = 0

    for user in stats:
        if stats[user][0] == call_date:
            size_sum += stats[user][1]

    return "Сумма за сегодня = " + str(size_sum) + " см"


def get_stats(date):
    global FILE

    with open(FILE, "r", encoding="utf-8") as f:
        stats = ast.literal_eval(f.read())

    f.close()

    call_date = str(date.date())
    call_day = str(date.date().day)
    call_month = str(date.date().month)
    call_year = str(date.date().year)

    daily_stats = ""

    return "Статистика за " + call_day + "." + call_month + "." + call_year + ":\n" + daily_stats
