from django.urls import path
from .views import create_question, create_preview

urlpatterns = [
    path('question/', create_question, name='create_question'),
    path('preview/', create_preview, name='create_preview'),
]