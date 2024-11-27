from django.urls import path
from .views import air_quality_view, air_quality_data, air_quality_map

urlpatterns = [
    path("air_quality/", air_quality_view, name="air_quality"),
    path('air-quality-data/', air_quality_data, name='air_quality_data'),
    path('map/', air_quality_map, name='air_quality_map'),
    #path("map/", map_view, name='map'),
]
