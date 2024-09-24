from django.contrib import admin

# Register your models here.
from .models import SensorData
from .models import BulbState

class BulbStateAdmin(admin.ModelAdmin):
    list_display = ('state', 'timestamp')  # Columns to display in the list view
    list_filter = ('state',)  # Add filters by state
    ordering = ('-timestamp',)  # Order by timestamp descending

# Register the model with the admin site
admin.site.register(BulbState, BulbStateAdmin)
# Register the SensorData model
@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'temperature', 'humidity')
    # list_filter = ('timestamp', 'temperature', 'humidity')
    # search_fields = ('temperature', 'humidity')