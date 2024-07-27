from rest_framework import serializers

class PromptSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=200)
    question = serializers.CharField(max_length=200)
    pdf = serializers.CharField(max_length=512, allow_blank=True)

class PreviewSerializer(serializers.Serializer):
    sentence = serializers.ListField(child=serializers.CharField(max_length=200))
    word = serializers.ListField(child=serializers.CharField(max_length=200))

class ChatbotSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=200)