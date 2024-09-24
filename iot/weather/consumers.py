import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import SensorData

class SensorConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        print("WebSocket connected")

    def disconnect(self, close_code):
        print("WebSocket disconnected")

    def receive(self, text_data):
        print(f"Received non-text or empty message: {text_data}")
        data = json.loads(text_data)    
        temperature = data['temperature']
        humidity = data['humidity']

        # Save to database
        SensorData.objects.create(temperature=temperature, humidity=humidity)

        # Send a response back
        self.send(text_data=json.dumps({
            'status': 'data received'
        }))


class clientConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        print("WebSocket connected")

    def disconnect(self, close_code):
        print(f"WebSocket disconnected with close code: {close_code}")

    def receive(self, text_data):
        print("Message received from WebSocket")

        # Fetch all sensor data from the database
        all_data = SensorData.objects.order_by('-timestamp')

        if all_data.exists():
            # Prepare the data as lists for temperature and humidity
            temperature_list = [entry.temperature for entry in all_data]
            humidity_list = [entry.humidity for entry in all_data]
            timestamp_list = [entry.timestamp.strftime('%Y-%m-%d %H:%M:%S') for entry in all_data]

            response_data = {
                'temperature': temperature_list,
                'humidity': humidity_list,
                'timestamps': timestamp_list
            }

            print(f"Sending data: {response_data}")
            self.send(text_data=json.dumps(response_data))
        else:
            print("No sensor data found in the database")
            self.send(text_data=json.dumps({
                'temperature': [],
                'humidity': [],
                'timestamps': [],
                'error': 'No data available'
            }))