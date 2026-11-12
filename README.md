# AirCheck — мониторинг качества воздуха

Веб-приложение на Django: сбор данных OpenWeather, расчёт AQI, карта (Leaflet) и графики (Chart.js).

## Требования
Python 3.12, PostgreSQL с PostGIS, Redis, библиотеки GEOS/GDAL.

## Запуск
```bash
pip install -r requirements.txt
cd env_monitoring
cp .env.example .env        # заполнить значения
python manage.py migrate
python manage.py runserver
```
Периодический сбор данных:
```bash
celery -A env_monitoring worker -l info
celery -A env_monitoring beat -l info
```

## Тесты
```bash
cd env_monitoring
python manage.py test monitoring
```

## Страницы
`/air_quality/`, `/map/`, `/air-quality-graph-page/`, `/air-quality-averages-page/`, `/aqi/`.
