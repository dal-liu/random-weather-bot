import tweepy
import requests
import json
import random
import math
import datetime
import csv
import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
TWITTER_API_KEY_SECRET = os.environ['TWITTER_API_KEY_SECRET']
BEARER_TOKEN = os.environ["BEARER_TOKEN"]
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
WEATHER_API_KEY = os.environ['WEATHER_API_KEY']


def get_city_id():
    with open("city.list.json", "r", encoding="utf-8") as f: # reset file name
        cities = json.load(f)
    city = random.choice(cities)
    return city['id']


def get_weather_dict(city_id):
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    url = f"{BASE_URL}id={city_id}&appid={WEATHER_API_KEY}&units=metric"
    return requests.get(url).json()


def get_condition(weather_id, description):
    if weather_id < 300:
        description = description.replace("thunderstorm", "thunderstorms")
    elif weather_id == 800:
        description = description.replace("sky", "skies")
    elif weather_id == 781:
        description = description.replace("tornado", "tornadoes")
    elif weather_id == 801:
        description = f"a {description}"
    return f"with {description}"


def get_emoji(weather_main, dt, sunrise, sunset):
    match weather_main:
        case "Thunderstorm":
            emoji = "\U000026C8"
        case "Drizzle":
            emoji = "\U0001F327"
        case "Rain":
            emoji = "\U0001F327"
        case "Snow":
            emoji = "\U0001F328"
        case "Tornado":
            emoji = "\U0001F32A"
        case "Clouds":
            emoji = "\U00002601"
        case "Clear":
            if sunrise <= dt < sunset:
                emoji = "\U00002600"
            else:
                emoji = "\U0001F319"
        case _:
            emoji = "\U0001F32B"
    return emoji


def get_country_name(country):
    with open("country codes.csv", "r") as csv_file: # reset file name
        reader = csv.reader(csv_file)
        countries_dict = {row[0]:row[1] for row in reader}
    return countries_dict[country]


def create_status(weather):
    temp_c_float = weather['main']['temp']
    temp_c = math.floor(temp_c_float)
    temp_f = math.floor((9/5) * temp_c_float + 32)

    weather_id = weather['weather'][0]['id']
    description = weather['weather'][0]['description']
    condition = get_condition(weather_id, description)

    name = weather['name']
    country_code = weather['sys']['country']
    country = get_country_name(country_code)

    unix_time = weather['dt'] + weather['timezone']
    local_time_24 = datetime.datetime.utcfromtimestamp(unix_time).strftime("%H:%M")
    local_time_12 = datetime.datetime.utcfromtimestamp(unix_time).strftime("%I:%M %p")
    if local_time_12[0] == "0":
        local_time_12 = local_time_12[1:]

    weather_main = weather['weather'][0]['main']
    sunrise = weather['sys']['sunrise']
    sunset = weather['sys']['sunset']
    emoji = get_emoji(weather_main, unix_time, sunrise, sunset)

    return f"{emoji} It's currently {temp_c}°C / {temp_f}°F {condition} in {name}, {country} as of {local_time_24} / {local_time_12} local time"


def tweet(status):
    client = tweepy.Client(BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    client.create_tweet(text=status)


def length_is_valid(status):
    return len(status) <= 280


if __name__ == "__main__":
    while True:
        status = create_status(get_weather_dict(get_city_id()))
        if length_is_valid(status):
            tweet(status)
            break