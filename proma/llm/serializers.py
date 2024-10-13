from rest_framework import serializers
from .models import message_tb

class PromptSerializer(serializers.Serializer):
    promptId = serializers.IntegerField(allow_null=True, required=False)
    chatroomId = serializers.IntegerField(allow_null=True)
    messageQuestion = serializers.CharField(max_length=10000)
    fileType = serializers.CharField(max_length=128, allow_blank=True)
    messageFile = serializers.CharField(max_length=512, allow_blank=True)

class EvalSerializer(serializers.Serializer):
    promptId = serializers.IntegerField(allow_null=True, required=False)

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = message_tb
        fields = '__all__'