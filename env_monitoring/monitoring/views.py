from django.shortcuts import render
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
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

    start_date = request.GET.get('start_date')  # Начальная дата
    end_date = request.GET.get('end_date')  # Конечная дата

    # Фильтрация данных по дате, если даты указаны
    if start_date:
        start_date = parse_datetime(start_date)
    if end_date:
        end_date = parse_datetime(end_date)

    data = PollutionData.objects.all()

    if start_date:
        data = data.filter(timestamp__gte=start_date)
    if end_date:
        data = data.filter(timestamp__lte=end_date)

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