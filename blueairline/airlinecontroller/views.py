from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
import datetime

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
        "destination_airports": destination_airports,
        "flights": flights
        })

def available_flights_by_date(request):
    flights_by_date = Flight.objects.order_by("departure_date")

    departure_airports = set()
    destination_airports = set()

    for flight in flights_by_date:
        departure_airports.add(flight.departure_airport)
        destination_airports.add(flight.destination_airport)

    return render(request, "airlinecontroller/index.html", {
        "departure_airports": departure_airports,
        "destination_airports": destination_airports,
        "flights": flights_by_date
        })
def available_flights_by_price_filtered(request):
    pass

def available_flights_by_date_filtered(request):
    pass
    
def available_flights_by_price(request):
    flights_by_price = Flight.objects.order_by("price")

    departure_airports = set()
    destination_airports = set()

    for flight in flights_by_price:
        departure_airports.add(flight.departure_airport)
        destination_airports.add(flight.destination_airport)

    return render(request, "airlinecontroller/index.html", {
        "departure_airports": departure_airports,
        "destination_airports": destination_airports,
        "flights": flights_by_price
        })

def init_seats(airplane):
    alphabet = ["A", "B", "C", "D", "E", "F"]

    for i in range(1, airplane.capacity + 1):
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


def split_date_input(date):
    #taking dates as string and splitting them for comparison - for form input
    date = str(date)
    date_base = date.split("T") #separate between the date and the time
    date_date = date_base[0].split("-") #separate the day month and year
    date_time = date_base[1].split(":") #separate the time for hours and minutes

    #day, month, year, hour (in 24 hour format), minutes
    return [date_date[2], date_date[1], date_date[0], date_time[0], date_time[1]]

def split_date_prev(date):
    #taking dates as string and splitting them for comparison - for existing database flights
    date = str(date)
    date_base = date.split(" ") #separate the date and time
    date_date = date_base[0].split("-") #separating the day month and year
    date_time = date_base[1].split(":") #separating the hours and minutes and seconds

    #day, month, year, hour (in 24 hour format), minutes
    return[date_date[2], date_date[1], date_date[0], date_time[0], date_time[1]]

def init_all_seats():
    airplanes = Airplane.objects.all()
    for airplane in airplanes:
        init_seats(airplane)

def hour_to_day(hours, minutes):
    hours = int(hours)
    minutes = int(minutes)
    return ((hours*60)+minutes)/(24*60)

def date_time_to_day(arr):
    day_sum_month = [31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
    result = int(arr[0]) + day_sum_month[int(arr[1])] + (int(arr[2])*365) + hour_to_day(arr[0], arr[1])
    return result

def reset_seats():
    flights = Flight.objects.all()
    for flight in flights:

        #convert the arrival date of the flight
        arr_date_arr = split_date_prev(flight.arrival_date)
        arrival_date = date_time_to_day(arr_date_arr)

        #convert today's date
        now = datetime.datetime.now()
        now_date_arr = split_date_prev(now)
        now_date = date_time_to_day(now_date_arr)

        #if the plane has landed, empty its seats and update ticket status
        if (arrival_date < now_date):
            seats = Seat.objects.filter(airplane=flight.airplane)
            tickets = Ticket.objects.filter(flight=flight)

            for seat in seats:
                seat.is_empty = True
                seat.save()
        
            for ticket in tickets:
                ticket.refund_status = "expired"
                ticket.save()


init_all_seats() #CREATE ALL SEATS FOR ALL AIRPLANES

#empty the seats of arrived flights
reset_seats()

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
        if (len(name_sur_arr) < 2):
            return render(request, "airlinecontroller/show_flight.html", {
                    "message": "Please enter your name and surname together.",
                    "flight": flightObject
                })

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
                seat_select, "active", 
                flightObject,
                Passenger.objects.get(name=name_sur_arr[0], surname=name_sur_arr[1], email_address=pass_mail_add, phone_number=pass_phone_num))
            ticketItem.save()

        except IntegrityError as e:
            print(e)
            return render(request, "airlinecontroller/index.html", {
                "message": "Ticket already exists."
            })

        except Passenger.DoesNotExist:
            return render(request, "airlinecontroller/show_flight.html", {
                    "message": "Please provide correct information. One or more of the passenger information you have entered is not correct.",
                    "flight": flightObject
                })

        return render(request, "airlinecontroller/show_feedback.html", {
            "pass_name_sur": pass_name_sur,
            "pass_phone_num": pass_phone_num,
            "pass_mail_add": pass_mail_add,
            "pass_card_num": pass_card_num,
            "pass_safety_pin": pass_safety_pin,
            "flight": flightObject,
            "seat_select": seat_select,
            "gate_number": flightObject.gate_number
        })
    else:
        return render(request, "airlinecontroller/index.html")

def available_flights(request):
    if request.method == "POST":
        departure_select = request.POST["departure_select"]
        destination_select = request.POST["destination_select"]
        dep_date_filter = request.POST["dep_date_filter"]

        #convert input date
        dep_date_filter_arr = split_date_input(dep_date_filter)
        input_dep_date = date_time_to_day(dep_date_filter_arr)

        #convert today's date
        now = datetime.datetime.now()
        now_date_arr = split_date_prev(now)
        now_date = date_time_to_day(now_date_arr)

        
        if (input_dep_date < now_date): #expired flights
            message = "You can not book a ticket for expired flights. Please select a departure date greater or equal to today."
            return render(request, "airlinecontroller/available_flights.html", {
            "message": message
        })
        else:
            available_flights = Flight.objects.filter(destination_airport=destination_select, departure_airport=departure_select, departure_date__gte=dep_date_filter)

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
    price = flightObject.price
    gate_number = flightObject.gate_number
    available_seats = Seat.objects.filter(airplane=airplane, is_empty=True)
    
    return render(request, "airlinecontroller/show_flight.html", {
            "f_dep_airport": f_dep_airport,
            "f_des_airport": f_des_airport,
            "f_dep_time": f_dep_time,
            "f_arr_time": f_arr_time,
            "flight": flightObject,
            "available_seats": available_seats,
            "gate_number": gate_number,
            "price": price
       })

def delete_flight(request, flight_id):
    
    flightObject = Flight.objects.get(pk=flight_id)
    flightObject.delete()

    flights = Flight.objects.all()
    departure_airports = set()
    destination_airports = set()

    for flight in flights:
        departure_airports.add(flight.departure_airport)
        destination_airports.add(flight.destination_airport)

    return render(request, "airlinecontroller/index.html", {
        "message": "The flight is deleted.",
        "departure_airports": departure_airports,
        "destination_airports": destination_airports,
        "flights": flights
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
        try:
            passengerObject = Passenger.objects.get(name=name_sur_arr[0], surname=name_sur_arr[1], phone_number=pass_phone_num, email_address=pass_mail_add)
        except Passenger.DoesNotExist:
            return render(request, "airlinecontroller/show_question_ticket_form.html", {
                "message": "Please provide correct information. There is no passenger matching with the information you have entered."
            })

        tickets = Ticket.objects.filter(passenger=passengerObject)
        if (len(tickets) == 0):
            return render(request, "airlinecontroller/show_tickets.html", {
            "tickets": tickets,
            "message": "You haven't booked a ticket yet. :("
            })
        else:
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
        try: 
            ticketObject = Ticket.objects.get(pk=pass_ticket_id)
            flightObject = ticketObject.flight
            seatObject = Seat.objects.get(seat_number=ticketObject.seat_number, airplane=flightObject.airplane)

            #ticket is refunded
            ticketObject.refund_status = "refunded"
            ticketObject.save()

            #the seat is available now
            seatObject.is_empty = True
            seatObject.save()

        except Ticket.DoesNotExist:
            return render(request, "airlinecontroller/show_refund_form.html", {
                "message": "Please provide correct information."
            })

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
        gate_number = request.POST["gate_number"]
        price = request.POST["price"]
        flight_scheduler = request.user
        #1- aynı tarihte iki uçusa aynı uçak kalkmaz & flight crew atanmaz - yapıldı
        #2- kalkan henüz inmediyse oluşturma 
        #3- indiyse de indiği havalimanından kalkabilir
        #4- kalktığı yere gidemez
        same_dep_flight = Flight.objects.filter(departure_date=dep_date)
        flights = Flight.objects.all()
        
        if same_dep_flight != None: #aynı anda kalkan uçuş varsa
            for flight in same_dep_flight:
                #aynı flight crew ya da airplane'i kullanamazlar
                if (flight.flight_crew.crew_name == flight_crew_name):
                    message = "Another flight which departures at the same time is using the same flight crew. Please select an available one."
                    is_valid = False

                elif flight.airplane.plane_name == airplane_name:
                    message = "Another flight which departures at the same time is using the same airplane. Please select an available one."
                    is_valid = False

                elif flight.flight_crew.crew_name == flight_crew_name and flight.airplane.plane_name == airplane_name:
                    message = "Another flight which departures at the same time is using the same airplane and flight crew. Please select available ones."
                    is_valid = False

        #CONVERTING INPUT DATE FOR COMPARISON
        dep_date_arr = split_date_input(dep_date)
        arr_date_arr = split_date_input(arr_date)

        dep_date_input = date_time_to_day(dep_date_arr) #departure date of input flight in days
        arr_date_input = date_time_to_day(arr_date_arr) #arrival date of input flight in days

        for flight in flights:
            #CONVERTING PREV DATES FOR COMPARISON
            prev_dep_date_arr = split_date_prev(flight.departure_date)
            prev_arr_date_arr = split_date_prev(flight.arrival_date)

            prev_dep_date = date_time_to_day(prev_dep_date_arr) #departure date of previous flight
            prev_arr_date = date_time_to_day(prev_arr_date_arr) #arrival date of previous flight

            print(f"prev_arr_date: {prev_arr_date}, dep_date_input: {dep_date_input}\n")

            """
            if the previous flight which uses the same crew or airplane hasn't landed, 
            a flight with the same crew or airplane can not depart
            """

            if prev_arr_date >= dep_date_input and flight.flight_crew.crew_name==flight_crew_name and flight.airplane.plane_name==airplane_name:
                message = "There is a previous flight which uses the same airplane and flight crew that hasn't landed yet. Please select available ones."
                is_valid = False

            elif prev_arr_date >= dep_date_input and flight.flight_crew.crew_name==flight_crew_name:
                message = "There is a previous flight which uses the same crew that hasn't landed yet. Please select an available flight crew."
                is_valid = False

            elif prev_arr_date >= dep_date_input and flight.airplane.plane_name==airplane_name:
                message = "There is a previous flight which uses the same airplane that hasn't landed yet. Please select an available airplane."
                is_valid = False

            
            """
            if the previous flight which uses the same crew or airplane has landed,
            the new flight with the same crew or airplane should depart from the same airport
            """
            if (prev_arr_date < dep_date_input and (flight.flight_crew.crew_name==flight_crew_name or flight.airplane.plane_name==airplane_name) and flight.destination_airport != dep_airport):
                message = "There is a flight that uses the same airplane or flight crew which has landed. You have to depart from the airport which the previous flight has landed."
                is_valid = False

            """
            only one flight can departure from a gate, multiple flights can not use the same gate
            """
            if (flight.gate_number == gate_number):
                message = "There is another flight which departures from the same gate. Please select an available gate."
                is_valid = False
        
        """
        destination and departure airport can not be the same
        """
        if (dep_airport == des_airport):
            message = "Destination and departure airport can not be the same."
            is_valid = False

        """
        a flight can not arrive to its destination before the departure date
        """
        if (dep_date >= arr_date):
            message = "A flight can not arrive before its departure date."
            is_valid = False


        if is_valid == True:
            try:
                flightItem = Flight.create_flight(
                    dep_airport, des_airport, dep_date, arr_date,
                    Airplane.objects.get(plane_name=airplane_name),
                    FlightCrew.objects.get(crew_name=flight_crew_name),
                    User.objects.get(username=flight_scheduler.username),
                    gate_number, price)
                flightItem.save()

            except IntegrityError as e:
                print(e)
                return render(request, "airlinecontroller/index.html", {
                    "message": "Flight already exists."
                })
            return HttpResponseRedirect(reverse("index"))
        else:
            if message:
                return render(request, "airlinecontroller/create_flight.html", {
                    "message": message,
                    "airplanes": Airplane.objects.all(),
                    "flight_crews": FlightCrew.objects.all()
                })
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