from django.db import models
from users.models import user_tb

# Create your models here.
class prompt_type_tb(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.BigIntegerField()

class prompt_tb(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(user_tb, on_delete=models.CASCADE)
    type_id = models.ForeignKey(prompt_type_tb, on_delete=models.CASCADE)
    prompt_title = models.CharField(max_length=256)
    prompt_description = models.CharField(max_length=256)
    prompt_preview = models.CharField(max_length=256)
    is_scrap = models.SmallIntegerField()
    emoji = models.CharField(max_length=256)
    prompt_category = models.SmallIntegerField()


class post_tb(models.Model):
    id = models.AutoField(primary_key=True)
    prompt_id = models.ForeignKey(prompt_tb, on_delete=models.CASCADE)
    post_title = models.CharField(max_length=256)
    post_description = models.CharField(max_length=256)
    create_at = models.DateTimeField(auto_now_add=True)

class like_tb(models.Model):
    id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey(post_tb, on_delete=models.CASCADE)
    user_id = models.ForeignKey(user_tb, on_delete=models.CASCADE)
    like_at = models.DateTimeField(auto_now_add=True)

class block_tb(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(user_tb, on_delete=models.CASCADE)
    type_id = models.ForeignKey(prompt_type_tb, on_delete=models.CASCADE)
    block_title = models.CharField(max_length=256)
    block_description = models.CharField(max_length=256)
    block_category = models.BigIntegerField()

class prompt_block_tb(models.Model):
    id = models.AutoField(primary_key=True)
    prompt_id = models.ForeignKey(prompt_tb, on_delete=models.CASCADE)
    block_id = models.ForeignKey(block_tb, on_delete=models.CASCADE)