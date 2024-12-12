from django.shortcuts import render
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.db.models import Avg
from datetime import datetime

from fontTools.misc.timeTools import timestampNow

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

    data = PollutionData.objects.filter(city_name=city_name)
    if start_date:
        data = data.filter(timestamp__gte=start_date)
    if end_date:
        data = data.filter(timestamp__lte=end_date)

    if not data.exists():
        return JsonResponse({'error': 'Нет данных для выбранного города или периода времени'}, status=404)

    result = data.values('timestamp', 'pm25', 'pm10', 'no2', 'co', 'so2')
    return JsonResponse(list(result), safe=False)

def air_quality_graph_page(request):

    unique_cities = get_cities()  # Сортируем без изменения регистра
    return render(request, 'monitoring/air_quality_graph.html', {'cities': unique_cities})

def air_quality_averages(request):
    city = request.GET.get('city')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not city:
        return JsonResponse({'error': 'Город не выбран'}, status=400)

    data = PollutionData.objects.filter(city_name=city)

    if start_date:
        data = data.filter(timestamp__gte=start_date)
    if end_date:
        data = data.filter(timestamp__lte=end_date)

    if not data.exists:
        return JsonResponse({'error': 'Нет данных'})

    averages = data.aggregate(
        avg_pm25=Avg('pm25'),
        avg_pm10=Avg('pm10'),
        avg_co=Avg('co'),
        avg_no2=Avg('no2'),
        avg_so2=Avg('so2')
    )

    return JsonResponse(averages)

def air_quality_averages_page(request):

    unique_cities = get_cities()  # Сортируем без изменения регистра
    return render(request, 'monitoring/air_quality_averages.html', {'cities': unique_cities})

def calculate_aqi_component(concentration, breakpoints):

    if concentration is None:
        return None

    for i in range(len(breakpoints) - 1):
        if breakpoints[i][0] <= concentration <= breakpoints[i + 1][0]:
            c_low, c_high = breakpoints[i][0], breakpoints[i + 1][0]
            i_low, i_high = breakpoints[i][1], breakpoints[i + 1][1]
            return ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low) + i_low

    return None

def calculate_aqi(pm25, pm10, co, no2, so2):
    breakpoints_pm25 = [
        (0, 0), (12, 50), (35.4, 100), (55.4, 150), (150.4, 200), (250.4, 300), (350.4, 400), (500.4, 500)
    ]
    breakpoints_pm10 = [
        (0, 0), (54, 50), (154, 100), (254, 150), (354, 200), (424, 300), (504, 400), (604, 500)
    ]
    breakpoints_co = [
        (0, 0), (4.4, 50), (9.4, 100), (12.4, 150), (15.4, 200), (30.4, 300), (40.4, 400), (50.4, 500)
    ]
    breakpoints_no2 = [
        (0, 0), (53, 50), (100, 100), (360, 150), (649, 200), (1249, 300), (1649, 400), (2049, 500)
    ]
    breakpoints_so2 = [
        (0, 0), (35, 50), (75, 100), (185, 150), (304, 200), (604, 300), (804, 400), (1004, 500)
    ]

    components = [
        calculate_aqi_component(pm25, breakpoints_pm25),
        calculate_aqi_component(pm10, breakpoints_pm10),
        calculate_aqi_component(co, breakpoints_co),
        calculate_aqi_component(no2, breakpoints_no2),
        calculate_aqi_component(so2, breakpoints_so2),
    ]

    return max(filter(None, components))

def aqi_view(request):
    city = request.GET.get('city')
    if not city:
        return JsonResponse({'error': 'Город не указан'}, status=400)

    try:
        # Получаем данные для указанного города
        data = PollutionData.objects.filter(city_name=city)
        if not data.exists():
            return JsonResponse({'error': f'Нет данных для города {city}'}, status=404)

        # Формируем список результатов с AQI
        results = []
        for record in data:
            aqi_value = calculate_aqi(record.pm25, record.pm10, record.co, record.no2, record.so2)
            results.append({
                'timestamp': record.timestamp,
                'aqi': aqi_value,
            })

        return JsonResponse({'aqi_results': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def aqi_page(request):
    # Получаем уникальный список городов из базы данных
    cities = get_cities()
    return render(request, 'monitoring/aqi_page.html', {'cities': cities})

def get_cities():
    cities = (
        PollutionData.objects.exclude(city_name__isnull=True)
        .exclude(city_name='')
        .values_list('city_name', flat=True)
        .distinct()
    )
    # Приводим названия городов к списку уникальных значений
    unique_cities = sorted(set(cities), key=lambda city: city.lower())

    return unique_cities