import enum


class SwitchIntEnum(enum.IntEnum):
    def switch(self):
        all_values = [i for i in self.__class__]
        next_value = self.value + 1
        if next_value in all_values:
            return self.__class__(next_value)
        return self.__class__(all_values[0].value)


class ChatCleanerChannelMessages(SwitchIntEnum):
    OFF = 0
    ON = 1


class ChatCleanerAdminMessages(SwitchIntEnum):
    OFF = 0
    ON = 1
