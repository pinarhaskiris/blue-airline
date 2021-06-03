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
    departure_airports = set()
    destination_airports = set()

    for flight in flights:
        departure_airports.add(flight.departure_airport)
        destination_airports.add(flight.destination_airport)
    
    return render(request, "airlinecontroller/index.html", {
        "departure_airports": departure_airports,
        "destination_airports": destination_airports
        })

def init_seats(airplane):
    alphabet = ["A", "B", "C", "D", "E", "F"]

    for i in range(airplane.capacity):
        for j in range(len(alphabet)):
            seat_number = str(i) + alphabet[j]
            prev_seats = Seat.objects.filter(seat_number=seat_number, airplane=airplane)

            if (len(prev_seats) == 0):
                try:
                    seatItem = Seat.create_seat(seat_number, airplane, True)
                    seatItem.save()

                except IntegrityError as e:
                    print(e)
                    return render(request, "airlinecontroller/index.html", {
                        "message": "Seat already exists."
                    })

def init_all_seats():
    airplanes = Airplane.objects.all()
    for airplane in airplanes:
        init_seats(airplane)

init_all_seats() #CREATE ALL SEATS FOR ALL AIRPLANES

def book_flight(request, flight_id):
    flightObject = Flight.objects.get(pk=flight_id)

    if request.method == "POST":
        pass_name_sur = request.POST["pass_name_sur"]
        pass_phone_num = request.POST["pass_phone_num"]
        pass_mail_add = request.POST["pass_mail_add"]
        pass_card_num = request.POST["pass_card_num"]
        pass_safety_pin = request.POST["pass_safety_pin"]
        seat_select = request.POST["seat_select"]

        #SELECTED SEAT IS OCCUPIED NOW
        airplane = flightObject.airplane
        seat = Seat.objects.get(airplane=airplane, seat_number=seat_select)
        seat.is_empty = False
        seat.save()

        name_sur_arr = pass_name_sur.split()

        #CREATE PASSENGER
        previous_passenger = Passenger.objects.filter(name=name_sur_arr[0], surname=name_sur_arr[1])
        if (len(previous_passenger) == 0):
            try:
                passengerItem = Passenger.create_passenger(
                    name_sur_arr[0], name_sur_arr[1], pass_mail_add, pass_phone_num)
                passengerItem.save()

            except IntegrityError as e:
                print(e)
                return render(request, "airlinecontroller/index.html", {
                    "message": "Passenger already exists."
                })

        #CREATE TICKET
        try:
            ticketItem = Ticket.create_ticket(
                seat_select, 100, 12, "active", 
                Flight.objects.get(pk=flight_id),
                Passenger.objects.get(name=name_sur_arr[0], surname=name_sur_arr[1], email_address=pass_mail_add, phone_number=pass_phone_num))
            ticketItem.save()

        except IntegrityError as e:
            print(e)
            return render(request, "airlinecontroller/index.html", {
                "message": "Ticket already exists."
            })


        return render(request, "airlinecontroller/show_feedback.html", {
            "pass_name_sur": pass_name_sur,
            "pass_phone_num": pass_phone_num,
            "pass_mail_add": pass_mail_add,
            "pass_card_num": pass_card_num,
            "pass_safety_pin": pass_safety_pin,
            "flight": flightObject,
            "seat_select": seat_select
        })
    else:
        return render(request, "airlinecontroller/index.html")

def available_flights(request):
    if request.method == "POST":
        departure_select = request.POST["departure_select"]
        destination_select = request.POST["destination_select"]

        available_flights = Flight.objects.filter(destination_airport=destination_select, departure_airport=departure_select)

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
    airplane = flightObject.airplane
    available_seats = Seat.objects.filter(airplane=airplane, is_empty=True)
    
    return render(request, "airlinecontroller/show_flight.html", {
            "f_dep_airport": f_dep_airport,
            "f_des_airport": f_des_airport,
            "f_dep_time": f_dep_time,
            "f_arr_time": f_arr_time,
            "flight": flightObject,
            "available_seats": available_seats
       })


def show_refund_form(request):
    return render(request, "airlinecontroller/show_refund_form.html")

def show_question_ticket_form(request):
    return render(request, "airlinecontroller/show_question_ticket_form.html")

def show_tickets(request):
    if request.method == "POST":
        pass_name_sur = request.POST["pass_name_sur"]
        pass_phone_num = request.POST["pass_phone_num"]
        pass_mail_add = request.POST["pass_mail_add"]

        name_sur_arr = pass_name_sur.split()

        passengerObject = Passenger.objects.get(name=name_sur_arr[0], surname=name_sur_arr[1], phone_number=pass_phone_num, email_address=pass_mail_add)
        tickets = passengerObject.tickets.all()

        return render(request, "airlinecontroller/show_tickets.html", {
            "tickets": tickets
        })

    else:
        return render(request, "airlinecontroller/index.html")


def update_ticket(request):
    if request.method == "POST":
        pass_name_sur = request.POST["pass_name_sur"]
        pass_phone_num = request.POST["pass_phone_num"]
        pass_mail_add = request.POST["pass_mail_add"]
        pass_ticket_id = request.POST["pass_ticket_id"]

        ticketObject = Ticket.objects.get(pk=pass_ticket_id)
        flightObject = ticketObject.flight
        seatObject = Seat.objects.get(seat_number=ticketObject.seat_number, airplane=flightObject.airplane)

        #ticket is refunded
        ticketObject.refund_status = "refunded"
        ticketObject.save()

        #the seat is available now
        seatObject.is_empty = True
        seatObject.save()

        return render(request, "airlinecontroller/refund_feedback.html")

    else:
        return render(request, "airlinecontroller/index.html")


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