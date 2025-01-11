from rest_framework import serializers
from .models import room_chat_tb, room_interview_tb

class IntroduceSerializer(serializers.Serializer):
    roomId = serializers.IntegerField(allow_null=True, required=False)
    characterId = serializers.IntegerField(allow_null=True, required=False)

class InterviewSerializer(serializers.Serializer):
    roomId = serializers.IntegerField(allow_null=True, required=False)
    characterId = serializers.IntegerField(allow_null=True, required=False)
    question = serializers.CharField(max_length=255, allow_blank=True)

class RoomChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = room_chat_tb
        fields = '__all__'

class RoomInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = room_interview_tb
        fields = '__all__'