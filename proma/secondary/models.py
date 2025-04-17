from django.db import models
from pgvector.django import VectorField

class block_history_log_pca_tb(models.Model):
    id = models.AutoField(primary_key=True)
    v_type = VectorField(dimensions=3)  # 3차원 벡터 필드
    v_category = VectorField(dimensions=3)  # 3차원 벡터 필드
    v_speaker = VectorField(dimensions=3)  # 3차원 벡터 필드
    v_listener = VectorField(dimensions=3)  # 3차원 벡터 필드
    v_instruction = VectorField(dimensions=3)  # 3차원 벡터 필드
    v_form = VectorField(dimensions=3)  # 3차원 벡터 필드
    v_excluded = VectorField(dimensions=3)  # 3차원 벡터 필드
    v_required = VectorField(dimensions=3)  # 3차원 벡터 필드
    o_type = models.CharField(max_length=255) # 3차원 벡터 필드
    o_category = models.CharField(max_length=255)
    o_speaker = models.CharField(max_length=255)
    o_listener = models.CharField(max_length=255)
    o_instruction = models.CharField(max_length=255)
    o_form = models.CharField(max_length=255)
    o_excluded = models.CharField(max_length=255)
    o_required = models.CharField(max_length=255)
    class Meta:
        app_label = 'secondary'  # 라우터가 이 앱을 secondary로 라우팅하도록 설정
        db_table = "block_history_log_pca_tb"  # 실제 PostgreSQL 테이블 이름
# Create your models here.
class block_history_log_embed_tb(models.Model):
    id = models.AutoField(primary_key=True)
    keyword = VectorField(dimensions=1024)
    class Meta:
        app_label = 'secondary'  # 라우터가 이 앱을 secondary로 라우팅하도록 설정
        db_table = "block_history_log_embed_tb"  # 실제 PostgreSQL 테이블 이름

