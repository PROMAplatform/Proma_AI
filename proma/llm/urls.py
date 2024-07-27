from django.urls import path
from .views import create_question, create_preview, dgu_question

urlpatterns = [
    path('question/', create_question, name='create_question'),
    path('preview/', create_preview, name='create_preview'),
    path('chatbot/', dgu_question, name='dgu_question'),
]