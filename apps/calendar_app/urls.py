from django.urls import path

from . import views

app_name = "calendar_app"

urlpatterns = [
    path("", views.CalendarMonthView.as_view(), name="month"),
    path("<int:year>/<int:month>/", views.CalendarMonthView.as_view(), name="month"),
    path("week/", views.CalendarWeekView.as_view(), name="week"),
    path("week/<int:year>/<int:month>/<int:day>/", views.CalendarWeekView.as_view(), name="week"),
]
