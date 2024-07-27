from random import randint


class SizeModule:
    @staticmethod
    def get_secret(max_chance):
        if randint(0, 99) < max_chance:
            return "(в жопе) "
        else:
            return ""

    @staticmethod
    def get_length(size):
        if randint(0, 14) == 9:
            return "как " + str(size / 4) + " гориллы"
        else:
            return str(size) + "см"