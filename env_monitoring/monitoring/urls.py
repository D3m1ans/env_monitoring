from django.urls import path
from .views import air_quality_view, air_quality_data, air_quality_map, air_quality_graph, air_quality_graph_page, \
    air_quality_averages, air_quality_averages_page, aqi_view, aqi_page

urlpatterns = [
    path("air_quality/", air_quality_view, name="air_quality"),
    path('air-quality-data/', air_quality_data, name='air_quality_data'),
    path('map/', air_quality_map, name='air_quality_map'),

    path('air-quality-graph/', air_quality_graph, name='air_quality_graph'),
    path('air-quality-graph-page/', air_quality_graph_page, name='air_quality_graph_page'),

    path('air-quality-averages/', air_quality_averages, name='air_quality_averages'),
    path('air-quality-averages-page/', air_quality_averages_page, name='air_quality_averages_page'),

    path('aqi/', aqi_page, name='aqi_page'),
    path('aqi/calculate/', aqi_view, name='calculate_aqi'),
]
