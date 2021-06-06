
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser): 
    pass

class Seat(models.Model):
    seat_number = models.CharField(max_length=5)
    airplane = models.ForeignKey("Airplane", on_delete=models.CASCADE, related_name="seats")
    is_empty = models.BooleanField(default=True)

    @classmethod
    def create_seat(cls, seat_number, airplane, is_empty):
        seatItem = cls(seat_number=seat_number, airplane=airplane, is_empty=is_empty)
        return seatItem

    def __str__(self):
        return f"{self.seat_number} of {self.airplane.plane_name}: Is Empty: {self.is_empty}"

class FlightCrew(models.Model):
    crew_name = models.CharField(max_length=64, default="")
    pilot = models.CharField(max_length=64)
    co_pilot = models.CharField(max_length=64)
    flight_engineer = models.CharField(max_length=64)
    navigator = models.CharField(max_length=64)
    flight_scheduler = models.ForeignKey("User", on_delete=models.CASCADE, related_name="crews")

    def __str__(self):
        return f"{self.crew_name}"


class Airplane(models.Model):
    plane_name = models.CharField(max_length=64, default="")
    plane_type = models.CharField(max_length=64)
    capacity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.plane_name}"

class Flight(models.Model):
    departure_airport = models.CharField(max_length=30)
    destination_airport = models.CharField(max_length=30)
    departure_date = models.DateTimeField("Departure Date")
    arrival_date = models.DateTimeField("Arrival Date")
    gate_number = models.CharField(max_length=10, default="")
    price = models.IntegerField(default=0)
    airplane = models.ForeignKey("Airplane", on_delete=models.CASCADE, related_name="flights")
    flight_crew = models.ForeignKey("FlightCrew", on_delete=models.CASCADE, related_name="flights")
    flight_scheduler = models.ForeignKey("User", on_delete=models.CASCADE, related_name="flights")

    @classmethod
    def create_flight(cls, departure_airport, destination_airport, departure_date, arrival_date, airplane, flight_crew, flight_scheduler, gate_number, price):
        flightItem = cls(departure_airport=departure_airport, destination_airport=destination_airport, departure_date=departure_date, arrival_date=arrival_date, airplane=airplane, flight_crew=flight_crew, flight_scheduler=flight_scheduler, gate_number=gate_number, price=price)
        return flightItem

    def __str__(self):
        return f"From: {self.departure_airport} to {self.destination_airport}"
"""
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
"""

class Passenger(models.Model):
    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    email_address = models.CharField(max_length=64)
    phone_number = models.IntegerField(default=0)

    @classmethod
    def create_passenger(cls, name, surname, email_address, phone_number):
        passengerItem = cls(name=name, surname=surname, email_address=email_address, phone_number=phone_number)
        return passengerItem

    def __str__(self):
        return f"{self.name} {self.surname}"

class Ticket(models.Model):
    seat_number = models.CharField(max_length=64)
    refund_status = models.CharField(max_length=64)
    flight = models.ForeignKey("Flight", on_delete=models.CASCADE, related_name="tickets")
    passenger = models.ForeignKey("Passenger", on_delete=models.CASCADE, related_name="tickets")

    @classmethod
    def create_ticket(cls, seat_number, refund_status, flight, passenger):
        ticketItem = cls(seat_number=seat_number, refund_status=refund_status, flight=flight, passenger=passenger)
        return ticketItem

    def __str__(self):
        return f"Seat Number: {self.seat_number} ID: {self.pk} Status: {self.refund_status}"


