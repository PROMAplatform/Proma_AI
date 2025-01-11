from django.urls import path
from .views import generate_introduce, generate_interview

urlpatterns = [
    path('introduce', generate_introduce, name='generate_introduce'),
    path('interview', generate_interview, name='generate_interview'),
]