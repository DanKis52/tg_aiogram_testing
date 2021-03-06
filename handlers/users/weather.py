import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
import requests
from data import config
from loader import dp
from states import Weather


@dp.message_handler(Command("weather"))
async def print_weather(message: types.Message):
    logging.info(
        f"{message.from_user.first_name, message.from_user.username, message.from_user.id} ввел {message.text}")
    await message.answer(text="Введи город, для выхода напиши /exit")
    await Weather.first()


@dp.message_handler(state=Weather.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    if message.text.lower() == "/exit" or message.text.lower() == "/exit@don_mafioznik_bot":
        logging.info(
            f"{message.from_user.first_name, message.from_user.username, message.from_user.id} вышел в меню")
        await state.finish()
        await message.answer(text="Ты вышел в меню")
    else:
        logging.info(
            f"{message.from_user.first_name, message.from_user.username, message.from_user.id} выбрал город {message.text}")
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        city = message.text
        complete_url = base_url + "appid=" + config.WEATHER_KEY + "&q=" + city
        response = requests.get(complete_url)
        full_weather_dict = response.json()
        if full_weather_dict['cod'] != "404":
            coord = full_weather_dict['coord']
            lon = coord['lon']
            lat = coord['lat']
            weather_main = full_weather_dict['main']
            temp = int(weather_main['temp'] - 273)
            feels_like = int(weather_main['feels_like'] - 273)
            humidity = weather_main['humidity']
            pressure = int(weather_main['pressure'] * 0.75006375541921)
            await message.answer_location(latitude=lat, longitude=lon)
            await message.answer(text=f"Погода в городе {city}:\n"
                                      f"Температура {temp} &#176C, ощущается как {feels_like} &#176C\n"
                                      f"Влажность {humidity} %\n"
                                      f"Давление {pressure} мм рт. ст.\n\n")
            await state.finish()
        else:
            await message.answer(text="Город не найден, попробуй снова или напиши /exit для выхода")
