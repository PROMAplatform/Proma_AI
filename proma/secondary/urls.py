from django.urls import path
from . import views

urlpatterns = [
    path('blockRecommend', views.block_recommend, name='blockRecommend'),
    path('blockRecommendRag', views.rag_block_recommend, name='blockRecommendRag'),
    path('saveBlock', views.save_block, name='saveBlock'),
] 