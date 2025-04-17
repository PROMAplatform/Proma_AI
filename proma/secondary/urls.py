from django.urls import path
from . import views

urlpatterns = [
    path('blockRecommend', views.block_recommend, name='blockRecommend'),
    path('saveBlock', views.save_block, name='saveBlock'),
] 