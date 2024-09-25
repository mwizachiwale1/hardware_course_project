from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('api/get-sensor-history/', views.get_sensor_history, name='get_sensor_history'),
  path('api/control-bulb/', views.control_bulb, name='control_bulb'),
  path('api/control-bulb-text-command/', views.control_bulb, name='control_bulb_text_command'),
  path('api/get-bulb-state/', views.get_bulb_state, name='get_bulb_state'),
]