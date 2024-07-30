from rest_framework import serializers

class PromptSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=200)
    question = serializers.CharField(max_length=200)
    file = serializers.CharField(max_length=128, allow_blank=True)
    url = serializers.CharField(max_length=512, allow_blank=True)

class PreviewSerializer(serializers.Serializer):
    sentence = serializers.ListField(child=serializers.CharField(max_length=200))
    word = serializers.ListField(child=serializers.CharField(max_length=200))