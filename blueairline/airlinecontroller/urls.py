from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_flight", views.create_flight, name="create_flight"),
    path("update_flight", views.update_flight, name="update_flight"),
    path("/<int:flight_id>", views.show_flight, name="show_flight"),
    path("available_flights", views.available_flights, name="available_flights"),
]