from django.urls import path
from . import views

app_name = "master"
urlpatterns = [
    path('holidays/', views.HolidaysView.as_view(), name='holidays'),
]
