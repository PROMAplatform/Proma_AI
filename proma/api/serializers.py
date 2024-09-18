from rest_framework import serializers
from users.models import chatroom_tb
from llm.models import message_tb

class QuestionSerializer(serializers.Serializer):
    userLoginId = serializers.CharField(max_length=1024)
    apiToken = serializers.CharField(max_length=1024)
    secretKey = serializers.CharField(max_length=1024)
    messageQuestion = serializers.CharField(max_length=1024)

class TestSerializer(serializers.Serializer):
    promptId = serializers.IntegerField(allow_null=True, required=False)
    chatroomId = serializers.IntegerField(allow_null=True)
    messageQuestion = serializers.CharField(max_length=10000)
    messageFile = serializers.CharField(max_length=512, allow_blank=True)

class ChatroomSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = chatroom_tb
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = message_tb
        fields = '__all__'