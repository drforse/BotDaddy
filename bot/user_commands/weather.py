from config import bot, geotoken, tf
from aiogram.types import Message
from ..core import Command
import traceback
from aiogram_bots_own_helper import log_err
from ..funcs import get_response_json
from pytz import timezone
from datetime import datetime


class Weather(Command):
    """
    get weather and time for a specific local specified as the command's argument
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
            tz = m.text.split()[1]
            if len(m.text.split()) > 2:
                for i in m.text.split()[2:]:
                    tz += ' ' + i
            lociq = 'https://eu1.locationiq.com/v1/search.php?key={}&q={}&format=json'.format(geotoken, tz)
            postal_lociq = 'https://eu1.locationiq.com/v1/search.php?key={}&postalcode={}&format=json'.format(
                geotoken, tz)
            response_json = await get_response_json(lociq)
            lat = float(response_json[0]['lat'])
            lon = float(response_json[0]['lon'])
            request = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&lang=ru&appid={OSM_API}'
            response_json = await get_response_json(request)
            try:
                weather_variables = []
                timezone_name = tf.timezone_at(lng=lon, lat=lat)
                if timezone_name is None:
                    timezone_name = tf.closest_timezone_at(lng=lon, lat=lat)
                zone = timezone(timezone_name)
                local = response_json['name']
                sunrise = str(datetime.fromtimestamp(response_json['sys']['sunrise'])).split()[1]
                sunset = str(datetime.fromtimestamp(response_json['sys']['sunset'])).split()[1]
                city_time = str(datetime.now(tz=zone))
                x = city_time.split()[1]
                if '+' in x:
                    x = x.split('+')[0]
                elif '-' in x:
                    x = x.split('-')[0]
                utc_format = str(datetime.now(tz=zone)).split(':')[2]
                if '+' in utc_format:
                    y = utc_format.split('+')[0]
                    utc_format = utc_format.split(y)[1]
                elif '-' in utc_format:
                    y = utc_format.split('-')[0]
                    utc_format = utc_format.split(y)[1]
                else:
                    utc_format = '+0'
                sec = str(float(x.split(':')[2]))
                secs = str(int(float(x.split(':')[2])))
                city_time = x.replace(sec, secs)
                wind_speed = response_json['wind']['speed']
                try:
                    wind_direction = response_json['wind']['deg']
                except KeyError:
                    wind_direction = None
                main_state = response_json['weather'][0]['description'].upper()
                temp = response_json['main']['temp']
                temp_F = round((temp - 273.15) * 9 / 5 + 32, 2)
                temp_C = round(temp - 273.15, 2)
                pressure = response_json['main']['pressure']
                humidity = response_json['main']['humidity']
                try:
                    visibility = response_json['visibility']
                except KeyError:
                    visibility = None
                clouds = response_json['clouds']['all']
                weather_message = f"*{local}*\n_Время: {city_time} UTC{utc_format}_\n_{main_state}_\nТемпература: {temp}ºK, {temp_F}ºF, {temp_C}ºC\nОблачность: {clouds}%\n" \
                                  f"Влажность: {humidity}%\nДавление: {pressure}hPa\nВидимость: {visibility}м\nСкорость и направление ветра:\n{wind_speed}м/с, {wind_direction}º\n" \
                                  f"Восход солнца: {sunrise} UTC+0\nЗаход солнца: {sunset} UTC+0"
                await bot.send_message(m.chat.id, weather_message, parse_mode='markdown')
            except KeyError:
                error_code = response_json['cod']
                error_message = response_json['message']
                message_text = f'Error {error_code}: {error_message}'
                await bot.send_message(m.chat.id, message_text)
        except Exception:
            await log_err(m=m, err=traceback.format_exc())
