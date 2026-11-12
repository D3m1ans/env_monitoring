from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from monitoring.services import data_fetcher
from monitoring.views import calculate_aqi, calculate_aqi_component

PM25 = [(0, 0), (12, 50), (35.4, 100)]


class AqiComponentTests(SimpleTestCase):
    def test_none_concentration_gives_none(self):
        self.assertIsNone(calculate_aqi_component(None, PM25))

    def test_breakpoint_values(self):
        self.assertEqual(calculate_aqi_component(0, PM25), 0)
        self.assertEqual(calculate_aqi_component(12, PM25), 50)

    def test_linear_interpolation(self):
        self.assertAlmostEqual(calculate_aqi_component(6, PM25), 25)

    def test_value_above_last_breakpoint_gives_none(self):
        self.assertIsNone(calculate_aqi_component(100, PM25))


class AqiTests(SimpleTestCase):
    def test_takes_maximum_subindex(self):
        aqi = calculate_aqi(pm25=6, pm10=54, co=0, no2=0, so2=0)
        self.assertEqual(aqi, 50)  # PM10 = 54 даёт 50, PM2.5 = 6 даёт 25

    def test_missing_pollutants_are_skipped(self):
        self.assertAlmostEqual(calculate_aqi(6, None, None, None, None), 25)

    def test_no_data_gives_none(self):
        self.assertIsNone(calculate_aqi(None, None, None, None, None))


def fake_get(geo_data, pollution_data):
    def get(url, **kwargs):
        response = Mock(status_code=200)
        response.json.return_value = geo_data if "geo" in url else pollution_data
        return response
    return get


class FetchDataTests(SimpleTestCase):
    GEO = [{"lat": 48.7, "lon": 44.5}]
    POLLUTION = {"list": [{"dt": 1700000000, "components": {
        "pm2_5": 7.2, "pm10": 7.5, "no2": 0.4, "co": 170.0, "so2": 1.9}}]}

    def test_fetch_returns_parsed_values(self):
        with patch.object(data_fetcher.requests, "get", fake_get(self.GEO, self.POLLUTION)):
            result = data_fetcher.fetch_air_pollution_data("Волгоград")
        self.assertEqual(result["pm25"], 7.2)
        self.assertEqual(result["coordinates"], {"lat": 48.7, "lon": 44.5})

    def test_unknown_city_raises(self):
        with patch.object(data_fetcher.requests, "get", fake_get([], {})):
            with self.assertRaises(ValueError):
                data_fetcher.fetch_air_pollution_data("Нигдеград")

    def test_save_without_pollution_list_raises(self):
        with patch.object(data_fetcher.requests, "get", fake_get(self.GEO, {"list": []})):
            with self.assertRaises(ValueError):
                data_fetcher.save_air_pollution_data("Волгоград")
