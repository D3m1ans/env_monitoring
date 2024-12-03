from celery import shared_task
from .services.data_fetcher import save_air_pollution_data

@shared_task
def fetch_and_save_air_quality():
    cities = ['Москва', 'Санкт-Петербург', 'Казань', 'Волгоград', 'Волжский', 'New York', 'London', 'Boston']
    print("Начало обработки городов")
    for city in cities:
        try:
            print(f"Обработка города: {city}")
            save_air_pollution_data(city)
            print(f"Данные для {city} обновлены")
        except Exception as e:
            print(f"Ошибка загрузки данных для {city}: {str(e)}")
    print("Обработка городов завершена")

@shared_task
def bar():
    return 'hello'