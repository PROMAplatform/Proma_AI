from rest_framework import serializers

class PromptSerializer(serializers.Serializer):
    promptId = serializers.IntegerField(allow_null=True)      # promptId
    messageQuestion = serializers.CharField(max_length=200)
    fileType = serializers.CharField(max_length=128, allow_blank=True)
    messageFile = serializers.CharField(max_length=512, allow_blank=True)

class PreviewSerializer(serializers.Serializer):
    sentence = serializers.ListField(child=serializers.CharField(max_length=200))
    word = serializers.ListField(child=serializers.CharField(max_length=200))