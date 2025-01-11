from django.db import models
import uuid

# Create your models here.

class user_tb(models.Model):
    id = models.BinaryField(primary_key=True, editable=False)
    chance_play = models.IntegerField(default=1)
    email = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255)
    provider = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    serial = models.CharField(max_length=255)
    class Meta:
        db_table = 'user_tb'

class character_tb(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    class Meta:
        db_table = 'character_tb'

class personalities_tb(models.Model):
    id = models.BigAutoField(primary_key=True)
    cautiousness = models.BigIntegerField()
    creativity = models.BigIntegerField()
    humor = models.BigIntegerField()
    logic = models.BigIntegerField()
    character = models.ForeignKey(character_tb, on_delete=models.CASCADE)
    class Meta:
        db_table = 'personalities_tb'

class category_tb(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    class Meta:
        db_table = 'category_tb'

class keyword_tb(models.Model):
    id = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(category_tb, on_delete=models.CASCADE)
    class Meta:
        db_table = 'keyword_tb'

class room_tb(models.Model):
    id = models.BigAutoField(primary_key=True)
    is_success = models.BooleanField()
    round = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    keyword = models.ForeignKey(keyword_tb, on_delete=models.CASCADE)
    user = models.ForeignKey(user_tb, on_delete=models.CASCADE)
    liar_character = models.ForeignKey(character_tb, on_delete=models.CASCADE)
    class Meta:
        db_table = 'room_tb'

class room_chat_tb(models.Model):
    id = models.BigAutoField(primary_key=True)
    chat_content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    character = models.ForeignKey(character_tb, on_delete=models.CASCADE)
    room = models.ForeignKey(room_tb, on_delete=models.CASCADE)
    class Meta:
        db_table = 'room_chat_tb'

class room_interview_tb(models.Model):
    id = models.BigAutoField(primary_key=True)
    answer = models.CharField(max_length=512)
    question = models.CharField(max_length=255)
    character = models.ForeignKey(character_tb, on_delete=models.CASCADE)
    room = models.ForeignKey(room_tb, on_delete=models.CASCADE)
    class Meta:
        db_table = 'room_interview_tb'
