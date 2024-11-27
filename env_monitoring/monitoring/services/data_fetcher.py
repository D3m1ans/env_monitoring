import requests
from django.contrib.gis.geos import Point
from django.utils.timezone import now
from datetime import datetime, timezone
from monitoring.models import PollutionData

API_KEY = "b1d12b01e343f1c3941a7e242c6c57c5"

def fetch_air_pollution_data(city_name):

    BASE_URL = f"http://api.openweathermap.org/data/2.5/air_pollution"

    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
    response = requests.get(geocoding_url)
    response.raise_for_status()
    geocoding_data = response.json()

    if not geocoding_data:
        raise ValueError(f"Город {city_name} не найден")

    latitude = geocoding_data[0]["lat"]
    longitude = geocoding_data[0]["lon"]

    pollution_url = f"{BASE_URL}?lat={latitude}&lon={longitude}&appid={API_KEY}"
    response = requests.get(pollution_url)
    response.raise_for_status()
    pollution_data = response.json()

    return {
        "city_name": city_name,
        "coordinates": {"lat": latitude, "lon": longitude},
        "timestamp": pollution_data["list"][0]["dt"],
        "pm25": pollution_data["list"][0]["components"]["pm2_5"],
        "pm10": pollution_data["list"][0]["components"]["pm10"],
        "no2": pollution_data["list"][0]["components"]["no2"],
        "co": pollution_data["list"][0]["components"]["co"],
        "so2": pollution_data["list"][0]["components"]["so2"],
    }

def save_air_pollution_data(city_name):

    GEO_URL = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
    POLLUTION_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

    # Получение координат города
    geo_response = requests.get(GEO_URL)
    if geo_response.status_code != 200:
        raise ValueError(f"Не удалось получить координаты города: {geo_response.text}")
    geo_data = geo_response.json()
    if not geo_data:
        raise ValueError("Город с указанным названием не найден.")

    lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]

    # Получение данных о загрязнении воздуха
    pollution_response = requests.get(
        POLLUTION_URL,
        params={"lat": lat, "lon": lon, "appid": API_KEY}
    )
    if pollution_response.status_code != 200:
        raise ValueError(f"Не удалось получить данные о загрязнении: {pollution_response.text}")
    pollution_data = pollution_response.json()

    if not pollution_data.get("list"):
        raise ValueError("Нет данных о загрязнении воздуха для данного города.")

    # Извлечение данных о качестве воздуха
    pollution_entry = pollution_data["list"][0]
    pm25 = pollution_entry["components"]["pm2_5"]
    pm10 = pollution_entry["components"]["pm10"]
    no2 = pollution_entry["components"]["no2"]
    co = pollution_entry["components"]["co"]
    so2 = pollution_entry["components"]["so2"]
    timestamp = datetime.fromtimestamp(pollution_entry["dt"], tz=timezone.utc)
    location = Point(lon, lat)

    # Проверка существующей записи
    existing_data = PollutionData.objects.filter(city_name=city_name).order_by("-timestamp").first()

    if existing_data and existing_data.timestamp == timestamp:
        # Если данные уже есть с таким же timestamp, ничего не делаем
        return

    # Сохранение данных в базе
    PollutionData.objects.update_or_create(
        city_name=city_name,
        timestamp=timestamp,
        defaults={
            "pm25": pm25,
            "pm10": pm10,
            "no2": no2,
            "co": co,
            "so2": so2,
            "location": location,
        }
    )