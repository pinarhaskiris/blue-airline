from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Flight, Passenger, Ticket, Airplane, Seat, FlightCrew

def index(request):
    # Authenticated users view their inbox
    flights = Flight.objects.all()

    return render(request, "airlinecontroller/index.html", {
        "flights": flights 
        })


def show_flight(request, flight_id):
    flightObject = Flight.objects.get(pk=flight_id)
    f_dep_airport = flightObject.departure_airport
    f_des_airport = flightObject.destination_airport
    f_dep_time = flightObject.departure_date
    f_arr_time = flightObject.arrival_date
    
    return render(request, "airlinecontroller/show_flight.html", {
            "f_dep_airport": f_dep_airport,
            "f_des_airport": f_des_airport,
            "f_dep_time": f_dep_time,
            "f_arr_time": f_arr_time
       })

def create_flight(request):
    crews = FlightCrew.objects.all()
    airplanes = Airplane.objects.all()
    return render(request, "airlinecontroller/create_flight.html", {
            "flight_crews": crews,
            "airplanes": airplanes
        })


def update_flight(request):
    if request.method == "POST":
        # Attempt to sign user in
        dep_airport = request.POST["dep_airport"]
        des_airport = request.POST["des_airport"]
        dep_date = request.POST["dep_date"]
        arr_date = request.POST["arr_date"]
        flight_crew = request.POST["flight_crew_select"]
        airplane = request.POST["airplane_select"]
        flight_scheduler = request.user

        try:
            flightItem = Flight.create_flight(
                dep_airport, des_airport, dep_date, arr_date,
                Airplane.objects.get(plane_type="Big"),
                FlightCrew.objects.get(pilot="Angelina"),
                User.objects.get(username=flight_scheduler.username))
            flightItem.save()

        except IntegrityError as e:
            print(e)
            return render(request, "airlinecontroller/index.html", {
                "message": "Flight already exists."
            })
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "airlinecontroller/index.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "airlinecontroller/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "airlinecontroller/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "airlinecontroller/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(email, email, password)
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "airlinecontroller/register.html", {
                "message": "Email address already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "airlinecontroller/register.html")