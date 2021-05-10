
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser): 
    pass

class Seat(models.Model):
    seat_number = models.CharField(max_length=5)
    airplane = models.ForeignKey("Airplane", on_delete=models.CASCADE, related_name="seats")

class FlightCrew(models.Model):
    pilot = models.CharField(max_length=64)
    co_pilot = models.CharField(max_length=64)
    flight_engineer = models.CharField(max_length=64)
    navigator = models.CharField(max_length=64)
    flight_scheduler = models.ForeignKey("User", on_delete=models.CASCADE, related_name="crews")

class Airplane(models.Model):
    plane_type = models.CharField(max_length=64)
    capacity = models.IntegerField(default=0)

class Flight(models.Model):
    departure_airport = models.CharField(max_length=5)
    destination_airport = models.CharField(max_length=5)
    departure_date = models.DateField("Departure Date")
    arrival_date = models.DateField("Arrival Date")
    airplane = models.ForeignKey("Airplane", on_delete=models.CASCADE, related_name="flights")
    flight_crew = models.ForeignKey("FlightCrew", on_delete=models.CASCADE, related_name="flights")
    flight_scheduler = models.ForeignKey("User", on_delete=models.CASCADE, related_name="flights")

    @classmethod
    def create_flight(cls, departure_airport, destination_airport, departure_date, arrival_date, airplane, flight_crew, flight_scheduler):
        flightItem = cls(departure_airport=departure_airport, destination_airport=destination_airport, departure_date=departure_date, arrival_date=arrival_date, airplane=airplane, flight_crew=flight_crew, flight_scheduler=flight_scheduler)
        return flightItem

    def serialize(self):
	    return  {
			"id": self.id,
			"departure_airport": self.departure_airport,
			"destination_airport": self.destination_airport,
			"departure_date": self.departure_date.strftime("%b %-d %Y, %-I:%M %p"),
			"arrival_date": self.arrival_date.strftime("%b %-d %Y, %-I:%M %p"),
            "airplane": self.airplane,
            "flight_crew": self.flight_crew,
            "flight_scheduler": self.flight_scheduler
        }


class Passenger(models.Model):
    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    email_address = models.CharField(max_length=64)
    phone_number = models.IntegerField(default=0)

class Ticket(models.Model):
    seat_number = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    gate_number = models.IntegerField(default=0)
    refund_status = models.CharField(max_length=64)
    flight = models.ForeignKey("Flight", on_delete=models.CASCADE, related_name="tickets")
    passenger = models.ForeignKey("Passenger", on_delete=models.CASCADE, related_name="tickets")



