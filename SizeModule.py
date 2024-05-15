from AbstractModule import AbstractModule

from random import randint


class SizeModule(AbstractModule):
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

    USERS = {}

    def __init__(self):
        super().__init__("size_mod")

    def activate(self):
        super(SizeModule, self).activate()

    def deactivate(self):
        super(SizeModule, self).deactivate()

    def get_messages(self):
        return self.MESSAGES

    def get_size(self, user_id, username, date):
        def get_secret(max_chance):
            if randint(0, 99) < max_chance:
                return "(в жопе) "
            else:
                return ""

        def get_length():
            if randint(0, 14) == 9:
                return "как " + str(self.USERS[user_id][2] / 4) + " гориллы"
            else:
                return str(self.USERS[user_id][2]) + "см"

        call_date = str(date.date())
        
        if user_id == "429951059650150411":
            self.USERS[user_id] = [username, call_date, 50, "", 0]

        if user_id == "318056725070741506":
            self.USERS[user_id] = [username, call_date, 15.5, "", 0]

        if user_id not in self.USERS:
            self.USERS[user_id] = [username, call_date, randint(1, 40), get_secret(1), 1]
        elif call_date != self.USERS[user_id][1]:
            chance = self.USERS[user_id][4]
            next_chance = 1

            secret = get_secret(chance)

            if secret == "":
                next_chance = min(chance + 1, 20)

            self.USERS[user_id] = [username, call_date, randint(1, 40), secret, next_chance]

        return \
            self.MESSAGES[randint(0, len(self.MESSAGES) - 1)] + " у тебя " + \
            self.USERS[user_id][3] + get_length()

    def get_chances(self, date):
        call_date = str(date.date())

        output = "Сегодняшние шансы (" + str(call_date) + "):\n"

        for user in self.USERS:
            if self.USERS[user][1] == call_date:
                output += ("\t" + self.USERS[user][0] + ":\t" + str(self.USERS[user][4]) + "%\n")

        return output

    def get_sum(self, date):
        call_date = str(date.date())

        sum = 0

        for user in self.USERS:
            if self.USERS[user][1] == call_date:
                sum += self.USERS[user][2]

        return "Сумма за сегодня = " + str(sum) + " см"

    def get_sizes(self, date):
        call_date = str(date.date())

        output = "Сегодняшние размеры (" + str(call_date) + "):\n"

        for user in self.USERS:
            if self.USERS[user][1] == call_date:
                output += ("\t" + self.USERS[user][0] + ":\t" + str(self.USERS[user][2]) + "см " + self.USERS[user][3] + "\n")

        return output
