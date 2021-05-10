from django.contrib import admin

# Register your models here.
from .models import Flight, FlightCrew, Passenger, Ticket, Seat, Airplane

# Register your models to admin site, then you can add, edit, delete and search your models in Django admin site.
admin.site.register(Flight)
admin.site.register(FlightCrew)
admin.site.register(Passenger)
admin.site.register(Ticket)
admin.site.register(Seat)
admin.site.register(Airplane)