from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from datetime import datetime

from .models import User, Flight, Passenger, Ticket, Airplane, Seat, FlightCrew


def index(request):
    # Authenticated users view their inbox
    flights = Flight.objects.all()

    return render(request, "airlinecontroller/index.html", {
        "flights": flights 
        })

def available_flights(request):
    if request.method == "POST":
        # Attempt to sign user in
        departure_select = request.POST["departure_select"]
        destination_select = request.POST["destination_select"]

        available_flights = Flight.objects.filter(departure_airport=departure_select).filter(destination_airport=destination_select)
        
        return render(request, "airlinecontroller/available_flights.html", {
            "available_flights": available_flights
        })

    else:
        return render(request, "airlinecontroller/index.html")

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
    is_valid = True

    if request.method == "POST":
        # Attempt to sign user in
        dep_airport = request.POST["dep_airport"]
        des_airport = request.POST["des_airport"]
        dep_date = request.POST["dep_date"]
        arr_date = request.POST["arr_date"]
        flight_crew_name = request.POST["flight_crew_select"]
        airplane_name = request.POST["airplane_select"]
        flight_scheduler = request.user
        #1- aynı tarihte iki uçusa aynı uçak kalkmaz & flight crew atanmaz - yapıldı
        #2- kalkan henüz inmediyse oluşturma 
        #3- indiyse de indiği havalimanından kalkabilir
        same_dep_flight = Flight.objects.filter(departure_date=dep_date)
        flights = Flight.objects.all()
        
        if same_dep_flight != None: #aynı anda kalkan uçuş varsa
            for flight in same_dep_flight:
                #aynı flight crew ya da airplane'i kullanamazlar
                if (flight.flight_crew.crew_name == flight_crew_name or flight.airplane.plane_name == airplane_name):
                    is_valid = False

        else: #aynı anda kalkan uçuş yoksa
            for flight in flights:
                #kalkan uçuş inmeden yeniden uçak kaldırılamaz
                if flight.arrival_date >= dep_date and (flight.airplane.plane_name == airplane_name or flight.flight_crew.crew_name == flight_crew_name):
                    is_valid = False
                
                #uçak indiyse de indiği yerden kaldırılmalı
                if (flight.airplane.plane_name == airplane_name or flight.flight_crew.crew_name == flight_crew_name) and flight.arrival_date <= dep_date and dep_airport != flight.destination_airport:
                    is_valid = False

        if is_valid == True:
            try:
                flightItem = Flight.create_flight(
                    dep_airport, des_airport, dep_date, arr_date,
                    Airplane.objects.get(plane_name=airplane_name),
                    FlightCrew.objects.get(crew_name=flight_crew_name),
                    User.objects.get(username=flight_scheduler.username))
                flightItem.save()

            except IntegrityError as e:
                print(e)
                return render(request, "airlinecontroller/index.html", {
                    "message": "Flight already exists."
                })
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "airlinecontroller/index.html", {
                "flights": flights 
            })
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