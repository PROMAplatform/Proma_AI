from django.urls import path
from .views import api_question, api_one_question

urlpatterns = [
    path('question', api_question, name='api_question'),
    path('one-question', api_one_question, name='api_one_question'),
]