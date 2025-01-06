from django.urls import path
from .views import create_question, prompt_evaluation, block_recommendation

urlpatterns = [
    path('question', create_question, name='create_question'),
    path('evaluation', prompt_evaluation, name='prompt_evaluation'),
    path('recommend', block_recommendation, name='block_recommend')
]