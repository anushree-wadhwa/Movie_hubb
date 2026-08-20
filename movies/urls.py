from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("movies/", views.movie_list, name="movie_list"),
    path("movies/<slug:slug>/", views.movie_detail, name="movie_detail"),
    path("movies/<slug:slug>/review/", views.review_create, name="review_create"),
    path("reviews/<int:review_id>/edit/", views.review_edit, name="review_edit"),
    path("reviews/<int:review_id>/report/", views.review_report, name="review_report"),
    path("bookings/", views.my_bookings, name="my_bookings"),
    path("bookings/<int:show_id>/book/", views.book_show, name="book_show"),
    path("bookings/<int:booking_id>/watched/", views.mark_watched, name="mark_watched"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
