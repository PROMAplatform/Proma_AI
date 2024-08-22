from django.urls import path
from .views import api_question

urlpatterns = [
    path('question', api_question, name='api_question'),
]