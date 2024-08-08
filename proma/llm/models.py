from django.db import models
from users.models import user_tb, chatroom_tb

# Create your models here.
class prompt_type_tb(models.Model):
    id = models.AutoField(primary_key=True)
    prompt_method = models.BigIntegerField()
    class Meta:
        db_table = 'prompt_type_tb'

class prompt_tb(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(user_tb, on_delete=models.CASCADE)
    prompt_method = models.ForeignKey(prompt_type_tb, on_delete=models.CASCADE)
    prompt_title = models.CharField(max_length=256)
    prompt_description = models.CharField(max_length=256)
    prompt_preview = models.CharField(max_length=256)
    is_scrap = models.SmallIntegerField()
    emoji = models.CharField(max_length=256)
    prompt_category = models.SmallIntegerField()
    class Meta:
        db_table = 'prompt_tb'


class post_tb(models.Model):
    id = models.AutoField(primary_key=True)
    prompt = models.ForeignKey(prompt_tb, on_delete=models.CASCADE)
    post_title = models.CharField(max_length=256)
    post_description = models.CharField(max_length=256)
    create_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'post_tb'

class like_tb(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(post_tb, on_delete=models.CASCADE)
    user = models.ForeignKey(user_tb, on_delete=models.CASCADE)
    like_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'like_tb'

class block_tb(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(user_tb, on_delete=models.CASCADE)
    prompt_method = models.ForeignKey(prompt_type_tb, on_delete=models.CASCADE)
    block_value = models.CharField(max_length=256)
    block_description = models.CharField(max_length=256)
    block_category = models.BigIntegerField()
    class Meta:
        db_table = 'block_tb'

class prompt_block_tb(models.Model):
    id = models.AutoField(primary_key=True)
    prompt = models.ForeignKey(prompt_tb, on_delete=models.CASCADE)
    block = models.ForeignKey(block_tb, on_delete=models.CASCADE)
    class Meta:
        db_table = 'prompt_block_tb'

class message_tb(models.Model):
    id = models.AutoField(primary_key=True)
    chatroom = models.ForeignKey(chatroom_tb, on_delete=models.CASCADE)
    prompt = models.ForeignKey(prompt_tb, on_delete=models.CASCADE)
    message_question = models.CharField(max_length=256)
    message_file = models.CharField(max_length=256, blank=True)
    message_create_at = models.DateField(auto_now_add=True)
    message_answer = models.CharField(max_length=1024)
    class Meta:
        db_table = 'message_tb'