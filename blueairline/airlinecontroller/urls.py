from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_flight", views.create_flight, name="create_flight"),
    path("update_flight", views.update_flight, name="update_flight"),
    path("<int:flight_id>", views.show_flight, name="show_flight"),
    path("available_flights", views.available_flights, name="available_flights"),
    path("book_flight/<int:flight_id>", views.book_flight, name="book_flight"),
    path("show_refund_form", views.show_refund_form, name="show_refund_form"),
    path("update_ticket", views.update_ticket, name="update_ticket"),
    path("show_question_ticket_form", views.show_question_ticket_form, name="show_question_ticket_form"),
    path("show_tickets", views.show_tickets, name="show_tickets"),
    path("delete_flight/<int:flight_id>", views.delete_flight, name="delete_flight"),
    path("available_flights_by_price", views.available_flights_by_price, name="available_flights_by_price"),
    path("available_flights_by_date", views.available_flights_by_date, name="available_flights_by_date")
]