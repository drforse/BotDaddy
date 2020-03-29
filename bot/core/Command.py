from config import bot, dp
from aiogram.dispatcher import Dispatcher
from aiogram import Bot
from aiogram.types import Message


class Command:
    def __init__(self, bot_: Bot = bot, dp_: Dispatcher = dp):
        self._bot = bot_
        self._dp = dp_

    @classmethod
    async def execute(cls, m: Message):
        if len(m.text.split()) > 1:
            await cls._execute_with_args(m)
            return

    @staticmethod
    async def _execute_with_args(m: Message):
        return

    def register(self, *custom_filters, commands=None, regexp=None,
                 content_types=None, state=None, run_task=None, **kwargs):
        self._dp.register_message_handler(self.execute, *custom_filters, commands=commands, regexp=regexp,
                                          content_types=content_types, state=state, run_task=run_task, **kwargs)

    def reg_callback(self, callback, *custom_filters, state=None, run_task=None, **kwargs):
        self._dp.register_callback_query_handler(callback, *custom_filters, state=None, run_task=None, **kwargs)

    def reg_message(self, callback, *custom_filters, commands=None, regexp=None,
                    content_types=None, state=None, run_task=None, **kwargs):
        self._dp.register_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                          content_types=content_types, state=state, run_task=run_task, **kwargs)
