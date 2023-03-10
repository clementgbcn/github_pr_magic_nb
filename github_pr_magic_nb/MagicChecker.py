import re
from enum import Enum
from collections import OrderedDict


class Rarity(Enum):
    LEVEL_1 = "Common", ":white_circle:"
    LEVEL_2 = "Uncommon", ":large_green_circle:"
    LEVEL_3 = "Rare", ":large_blue_circle:"
    LEVEL_4 = "Epic", ":large_purple_circle:"
    LEVEL_5 = "Legendary", ":large_orange_circle:"
    LEVEL_6 = "e-tech", ":large_yellow_circle:"
    LEVEL_7 = "Seraph", ":red_circle:"
    LEVEL_8 = "Pearlescent", ":large_brown_circle:"
    LEVEL_9 = "Rainbow", ":black_circle:"
    LEVEL_10 = "God", ":unicorn_face:"

    @property
    def level_value(self):
        return self.name.replace("_", " ").lower().capitalize()
    @property
    def level_name(self):
        return self.value[0]

    @property
    def symbol(self):
        return self.value[1]

    def get_str_repr(self):
        return "{} {} - {}".format(self.symbol, self.level_value, self.level_name)

    @staticmethod
    def get_scarcity(value):
        levels = list(Rarity)
        if value < 100:
            # Do not process non-active repositories
            return Rarity.LEVEL_1
        value_str = str(value)
        # One digit only followed by multiple zero
        if re.fullmatch(r"\d0+", value_str):
            return levels[len(value_str) - 2]
        # Divisible by 1000
        if value % 1000 == 0:
            # Get number of zero
            nb_zero = Rarity.get_nb_zero(value)
            return levels[nb_zero - 2]
        for i in range(len(value_str) - 1):
            if value_str[i] != value_str[i + 1]:
                return Rarity.LEVEL_1
        return levels[len(value_str) - 2]

    @staticmethod
    def get_nb_zero(value):
        nb_zero = 0
        while value % 10 == 0:
            value = value // 10
            nb_zero += 1
        return nb_zero

    @staticmethod
    def check_rarity_value_range(start, end):
        rarity_levels = OrderedDict()
        for i in range(start, end):
            if Rarity.get_scarcity(i) != Rarity.LEVEL_1:
                rarity_levels[i] = Rarity.get_scarcity(i)
        return rarity_levels
