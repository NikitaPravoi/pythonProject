from django.contrib import admin
from django.urls import path,include
from .views import index

from . import main
urlpatterns = [
    path('', index),
]