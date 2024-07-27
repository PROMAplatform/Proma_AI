from django.db import models
from llm.models import prompt_tb

class user_tb(models.Model):
    id = models.AutoField(primary_key=True)
    user_login_id = models.CharField(max_length=256)
    user_name = models.CharField(max_length=256)
    user_login_method = models.SmallIntegerField()
    create_at = models.DateTimeField(auto_now_add=True)
    user_ongoing = models.BooleanField(default=False)

class chatroom_tb(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(user_tb, on_delete=models.CASCADE)
    chatroom_title = models.CharField(max_length=256)
    create_at = models.DateTimeField(auto_now_add=True)
    emoji = models.CharField(max_length=128)

class message_tb(models.Model):
    id = models.AutoField(primary_key=True)
    chatroom_id = models.ForeignKey(chatroom_tb, on_delete=models.CASCADE)
    prompt_id = models.ForeignKey(prompt_tb, on_delete=models.CASCADE)
    message_question = models.CharField(max_length=256)
    message_file = models.CharField(max_length=256)
    message_create_at = models.DateTimeField(auto_now_add=True)
    message_answer = models.CharField(max_length=256)