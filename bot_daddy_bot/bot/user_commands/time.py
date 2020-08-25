from ...config import bot, geotoken, tf
from aiogram.types import Message
from ..core import Command
from datetime import datetime, timedelta
from ..funcs import get_response_json
from ...aiogram_bots_own_helper import log_err
from pytz import timezone
import traceback


class Time(Command):
    """
    get time for a specific local or by UTF/GMT specified as the command's argument
    """
    def __init__(self):
        super().__init__()

    @classmethod
    async def execute(cls, m: Message):
        if len(m.text.split()) > 1:
            await cls._execute_with_args(m)
            return

    @staticmethod
    async def _execute_with_args(m: Message):
        try:
            if 'UTC' in m.text or 'GMT' in m.text:
                utc_format = m.text.split()[1]
                increment = utc_format.split('UTC')[1] if 'UTC' in utc_format else utc_format.split('GMT')[1]
                increment = int(increment) if increment != '' else 0
                if increment > 14 or increment < -12:
                    raise TypeError('Invalid UTC or GMT format!')
                else:
                    dt = datetime.utcnow() + timedelta(hours=increment)
            else:
                tz = m.text.split()[1]
                if len(m.text.split()) > 2:
                    for i in m.text.split()[2:]:
                        tz += ' ' + i
                lociq = 'https://eu1.locationiq.com/v1/search.php?key={}&q={}&format=json'.format(geotoken, tz)
                postal_lociq = 'https://eu1.locationiq.com/v1/search.php?key={}&postalcode={}&format=json'.format(
                    geotoken,
                    tz)
                response_json = await get_response_json(lociq)
                lat = float(response_json[0]['lat'])
                lon = float(response_json[0]['lon'])
                timezone_name = tf.timezone_at(lng=lon, lat=lat)
                if timezone_name is None:
                    timezone_name = tf.closest_timezone_at(lng=lon, lat=lat)
                zone = timezone(timezone_name)
                dt = datetime.now(tz=zone)
                utc_format = str(datetime.now(tz=zone)).split(':')[2]
                if '+' in utc_format:
                    x = utc_format.split('+')[0]
                    utc_format = utc_format.split(x)[1]
                elif '-' in utc_format:
                    x = utc_format.split('-')[0]
                    utc_format = utc_format.split(x)[1]
                else:
                    utc_format = '+0'
                utc_format = f'UTC{utc_format}'
            dt = dt.strftime('%H:%M:%S')
            if 'UTC' not in m.text and 'GMT' not in m.text:
                time_format = 'В {} сейчас:\n {} {}'.format(tz, dt, utc_format)
            elif 'UTC' in m.text:
                time_format = f'По {utc_format} сейчас:\n {dt}'
            else:
                time_format = f'По {utc_format} сейчас:\n {dt}'
            await bot.send_message(m.chat.id, time_format, reply_to_message_id=m.message_id)
        except TypeError:
            await bot.send_message(m.chat.id, 'Invalid UTC/GMT format')
        except:
            await log_err(m=m, err=traceback.format_exc())
