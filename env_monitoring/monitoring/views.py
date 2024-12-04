from django.shortcuts import render
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from django.db.models import Func
from datetime import datetime

from .services.data_fetcher import save_air_pollution_data
from .models import PollutionData



# Create your views here.

def air_quality_view(request):
    context = {}

    if request.method == "POST":
        city_name = request.POST.get("city")  # Получаем название города из формы

        if not city_name:
            context["error"] = "Название города не указано."
        else:
            try:
                # Сохраняем данные с помощью функции из data_fetcher
                save_air_pollution_data(city_name)

                # Получаем последнюю запись из базы данных для указанного города
                data = PollutionData.objects.filter(city_name=city_name).order_by("-timestamp").first()

                if data:
                    context["success"] = f"Данные о качестве воздуха в городе {city_name} успешно загружены."
                    context["data"] = {
                        "city": data.city_name,
                        "timestamp": data.timestamp.isoformat(),  # Конвертация в ISO-формат для отображения
                        "pm25": data.pm25,
                        "pm10": data.pm10,
                        "no2": data.no2,
                        "co": data.co,
                        "so2": data.so2,
                    }
                else:
                    context["error"] = "Не удалось найти данные для указанного города."
            except Exception as e:
                context["error"] = f"Произошла ошибка: {str(e)}"

    return render(request, "monitoring/air_quality.html", context)

def air_quality_data(request):
    # Выбираем данные с координатами и параметрами загрязнений

    start_datetime = request.GET.get('start_datetime')  # Начальная дата
    end_datetime = request.GET.get('end_datetime')  # Конечная дата

    # Фильтрация данных по дате, если даты указаны
    if start_datetime:
        start_datetime = parse_datetime(start_datetime)
    if end_datetime:
        end_datetime = parse_datetime(end_datetime)

    data = PollutionData.objects.all()

    if start_datetime:
        data = data.filter(timestamp__gte=start_datetime)
    if end_datetime:
        data = data.filter(timestamp__lte=end_datetime)

    features = []
    for entry in data:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [entry.location.x, entry.location.y]  # Широта и долгота
            },
            "properties": {
                "city_name": entry.city_name,
                "pm25": entry.pm25,
                "pm10": entry.pm10,
                "no2": entry.no2,
                "co": entry.co,
                "so2": entry.so2,
                "timestamp": entry.timestamp.isoformat()
            }
        })

    return JsonResponse({
        "type": "FeatureCollection",
        "features": features
    })

def air_quality_map(request):
    return render(request, 'monitoring/air_quality_map.html')

def air_quality_graph(request):
    # Получаем параметры запроса
    city_name = request.GET.get('city', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Отладка: выводим параметры
    print(f"City: {city_name}, Start Date: {start_date}, End Date: {end_date}")

    # Фильтруем данные
    data = PollutionData.objects.filter(city_name=city_name)
    if start_date:
        data = data.filter(timestamp__gte=start_date)
    if end_date:
        data = data.filter(timestamp__lte=end_date)

    # Проверка наличия данных
    if not data.exists():
        return JsonResponse({'error': 'Нет данных для выбранного города или периода времени'}, status=404)

    # Возвращаем данные
    result = data.values('timestamp', 'pm25', 'pm10', 'no2', 'co', 'so2')
    return JsonResponse(list(result), safe=False)

def air_quality_graph_page(request):
    # Получаем уникальные города из базы данных
    cities = (
        PollutionData.objects.exclude(city_name__isnull=True)
        .exclude(city_name='')
        .values_list('city_name', flat=True)
        .distinct()
    )
    # Приводим названия городов к списку уникальных значений
    unique_cities = sorted(set(cities), key=lambda city: city.lower())  # Сортируем без изменения регистра
    return render(request, 'monitoring/air_quality_graph.html', {'cities': unique_cities})

class Lower(Func):
    function = 'LOWER'