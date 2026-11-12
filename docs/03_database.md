# База данных

СУБД: PostgreSQL с расширением PostGIS (система координат WGS84, EPSG:4326).

## Таблица `PollutionData` (`monitoring_pollutiondata`)
| Поле | Тип | Описание |
|---|---|---|
| `city_name` | varchar(100), null | название города |
| `location` | PointField (PostGIS) | точка: широта и долгота |
| `pm25` | float, null | PM2.5 |
| `pm10` | float, null | PM10 |
| `no2` | float, null | диоксид азота |
| `co` | float, null | угарный газ |
| `so2` | float, null | диоксид серы |
| `timestamp` | datetime | время измерения |

Сортировка по умолчанию — по `timestamp`. Дубликаты исключаются проверкой пары (`city_name`, `timestamp`) при сохранении.

## Планируется
Поле `o3` (озон) — отдельной задачей.
