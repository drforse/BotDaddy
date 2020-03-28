from config import col2, bot, bot_id
from aiogram_bots_own_helper import log_err
import traceback
import requests


async def anti_flood(message):
    try:
        if message.from_user.id not in col2.find_one({'users': {'$exists': True}})['users']:
            col2.update_one({'users': {'$exists': True}},
                            {'$push': {'users': message.from_user.id}})
            col2.update_one({'users': {'$exists': True}},
                            {'$set': {str(message.from_user.id): 1}})
        elif col2.find_one({'users': {'$exists': True}})[str(message.from_user.id)] < 6:
            col2.update_one({'users': {'$exists': True}},
                            {'$inc': {str(message.from_user.id): 1}},
                            upsert=True)
        elif col2.find_one({'users': {'$exists': True}})[str(message.from_user.id)] == 6:
            await bot.send_message(message.chat.id, 'Хватит страдать хуйней!')
            col2.update_one({'users': {'$exists': True}},
                            {'$inc': {str(message.from_user.id): 1}},
                            upsert=True)
        bot_member = await bot.get_chat_member(message.chat.id, bot_id)
        if bot_member.can_delete_messages:
            await bot.delete_message(message.chat.id, message.message_id)
    except:
        await log_err(m=message, err=traceback.format_exc())


async def get_response_json(request):
    response = requests.get(request)
    return response.json()
