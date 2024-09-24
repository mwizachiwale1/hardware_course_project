from django.shortcuts import render
from django.http import JsonResponse
from .models import SensorData, BulbState, UserAction
import json
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(request):
  return render(request, 'weather/index.html')


def get_sensor_history(request):
    # Fetch the latest 20 records from the database
    sensor_data = SensorData.objects.order_by('-timestamp')[:20]
    data = [{
        'timestamp': entry.timestamp,
        'temperature': entry.temperature,
        'humidity': entry.humidity
    } for entry in sensor_data]
    return JsonResponse(data, safe=False)


def get_bulb_state(request):
    # Retrieve the latest bulb state from the database
    try:
        bulb_state = BulbState.objects.latest('timestamp').state
    except BulbState.DoesNotExist:
        # Default state if no record exists
        bulb_state = 'off'

    return JsonResponse({'state': bulb_state})

@csrf_exempt
def control_bulb(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data.get('action').lower();
        bulb_action = ""
        motor_action = ""
        if "on" in text and "bulb" in text:
            bulb_action = "TURN_ON"
        elif "off" in text and "bulb" in text:
            bulb_action = "TURN_OFF"
        elif "on" in text and "motor" in text:
            motor_action = "TURN_ON"
        elif "off" in text and "motor" in text:
            motor_action = "TURN_OFF"
        else:
            return JsonResponse({'message': f'Bulb turned {motor_action.split("_")[1]}', 'id': user_action.id})

        user_action = UserAction.objects.create(action=action)

        # Business Logic: Update bulb state based on user action
        if action == 'TURN_ON':
            BulbState.objects.create(state='ON')
        elif action == 'TURN_OFF':
            BulbState.objects.create(state='OFF')

        return JsonResponse({'message': f'Bulb turned {action.split("_")[1]}', 'id': user_action.id})
