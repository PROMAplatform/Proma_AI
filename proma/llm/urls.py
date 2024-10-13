from django.urls import path
from .views import create_question, create_preview, prompt_evaluation

urlpatterns = [
    path('question', create_question, name='create_question'),
    path('evaluation', prompt_evaluation, name='prompt_evaluation'),
    path('preview', create_preview, name='create_preview'),
]