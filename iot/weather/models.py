from django.db import models
from django.http import JsonResponse

class SensorData(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField()
    humidity = models.FloatField()

    def __str__(self):
        return f"Temp: {self.temperature}, Humidity: {self.humidity}"


class UserAction(models.Model):
    action_choices = [
        ('TURN_ON', 'Turn On'),
        ('TURN_OFF', 'Turn Off'),
    ]
    action = models.CharField(max_length=8, choices=action_choices)  # User action
    timestamp = models.DateTimeField(auto_now_add=True)  # Time of action

    def __str__(self):
        return f"User Action: {self.action} at {self.timestamp}"


def get_sensor_history(request):
    # Fetch the latest 20 records from the database
    sensor_data = SensorData.objects.order_by('-timestamp')[:20]
    data = [{
        'timestamp': entry.timestamp,
        'temperature': entry.temperature,
        'humidity': entry.humidity
    } for entry in sensor_data]
    return JsonResponse(data, safe=False)



class BulbState(models.Model):
    state_choices = [
        ('ON', 'On'),
        ('OFF', 'Off'),
    ]
    state = models.CharField(max_length=3, choices=state_choices)  # Bulb state: ON/OFF
    timestamp = models.DateTimeField(auto_now_add=True)  # Time of state change

    def __str__(self):
        return f"Bulb is {self.state} at {self.timestamp}"
