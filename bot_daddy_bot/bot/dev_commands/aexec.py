import traceback

from aiogram.types import Message
from aiogram import exceptions

from ..core import Command
from ...config import bot
from ...aiogram_bots_own_helper import parse_asyncio


class Aexec(Command):
    """
    don't even think about it, it is only for devs
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        if len(m.text.split()) > 1:
            await cls._execute_with_args(m)
            return
        try:
            async_func_name = "__async_exec_function"
            code = await parse_asyncio(
                m.reply_to_message.text,
                func_name=async_func_name,
                message_var_name="m")
            exec(code)
            await locals()[async_func_name](m)
        except Exception as e:
            try:
                await m.answer(traceback.format_exc())
            except exceptions.MessageIsTooLong:
                await m.answer(str(e))

    @staticmethod
    async def _execute_with_args(m: Message):
        try:
            async_func_name = "__async_exec_function"
            code = await parse_asyncio(
                m.get_args(),
                func_name=async_func_name,
                message_var_name="m")
            exec(code)
            await locals()[async_func_name](m)
        except Exception as e:
            try:
                await m.answer(traceback.format_exc())
            except exceptions.MessageIsTooLong:
                await m.answer(str(e))
