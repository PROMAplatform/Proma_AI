from django.db import models

class user_tb(models.Model):
    id = models.AutoField(primary_key=True)
    user_login_id = models.CharField(max_length=256)
    user_name = models.CharField(max_length=256)
    user_login_method = models.SmallIntegerField()
    create_at = models.DateTimeField(auto_now_add=True)
    user_ongoing = models.BooleanField(default=False)
    class Meta:
        db_table = 'user_tb'

class chatroom_tb(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(user_tb, on_delete=models.CASCADE)
    chat_room_title = models.CharField(max_length=256)
    create_at = models.DateTimeField(auto_now_add=True)
    emoji = models.CharField(max_length=128)
    class Meta:
        db_table = 'chatroom_tb'