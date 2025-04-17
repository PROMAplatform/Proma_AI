from django.db import models
from pgvector.django import VectorField

class block_history_log_tb(models.Model):
    id = models.AutoField(primary_key=True)
    history = VectorField(dimensions=3)  # 3차원 벡터 필드
    prompt_category = models.CharField(max_length=255)
    prompt_method = models.CharField(max_length=255)
    prompt_description = models.CharField(max_length=255)
    class Meta:
        app_label = 'secondary'  # 라우터가 이 앱을 secondary로 라우팅하도록 설정
        db_table = "block_history_log_tb"  # 실제 PostgreSQL 테이블 이름
# Create your models here.


