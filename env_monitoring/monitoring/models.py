from django.contrib.gis.db import models


# Create your models here.

class PollutionData(models.Model):
    city_name = models.CharField(max_length=100, null=True, blank=True)
    location = models.PointField()
    pm25 = models.FloatField(null=True, blank=True)
    pm10 = models.FloatField(null=True, blank=True)
    no2 = models.FloatField(null=True, blank=True)
    co = models.FloatField(null=True, blank=True)
    so2 = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"Data as {self.timestamp} | Location {self.location}"