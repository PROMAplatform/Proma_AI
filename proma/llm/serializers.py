from rest_framework import serializers
from .models import message_tb

class PromptSerializer(serializers.Serializer):
    promptId = serializers.IntegerField(allow_null=True)      # promptId
    chatroomId = serializers.IntegerField(allow_null=True)
    messageQuestion = serializers.CharField(max_length=200)
    fileType = serializers.CharField(max_length=128, allow_blank=True)
    messageFile = serializers.CharField(max_length=512, allow_blank=True)

class PreviewSerializer(serializers.Serializer):
    sentence = serializers.ListField(child=serializers.CharField(max_length=200))
    word = serializers.ListField(child=serializers.CharField(max_length=200))

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = message_tb
        fields = '__all__'