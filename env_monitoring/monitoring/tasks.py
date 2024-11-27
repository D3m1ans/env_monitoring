from celery import shared_task
from .services.data_fetcher import save_air_pollution_data

@shared_task
def update_air_quality_data():
    cities = ["Москва", "Казань", "Санкт-Петербург", "Волгоград", "Волжский", "New York", "Boston", "London"]

    for city in cities:
        try:
            save_air_pollution_data(city)
            print(f"Данные для города {city} обновлены")
        except Exception as e:
            print(f"Ошибка при обновлении данных для города {city}: {str(e)}")
