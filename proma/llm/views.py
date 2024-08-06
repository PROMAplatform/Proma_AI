from django.shortcuts import render
from .serializers import PromptSerializer, PreviewSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .utils import gemini_answer, gemini_preview, chat_img
from .models import prompt_tb

@api_view(['POST'])
def create_question(request):
    serializer = PromptSerializer(data=request.data)
    if serializer.is_valid():
        promptId = serializer.data['promptId']
        prompt = prompt_tb.objects.get(pk=promptId).prompt_preview
        messageQuestion = serializer.data['messageQuestion']
        messageFile = serializer.data['messageFile']
        fileType = serializer.data['fileType']
        if fileType == "image":
            answer = chat_img(prompt, messageQuestion, messageFile)
        else:
            answer = gemini_answer(prompt, messageQuestion, messageFile)
        return Response({
            "responseDto" : {
                "messageAnswer": answer
            },
            "error":None,
            "success": True
        },status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_preview(request):
    serializer = PreviewSerializer(data=request.data)
    if serializer.is_valid():
        if (len(serializer.data['sentence']) != len(serializer.data['word'])):
            return Response({
                "responseDto" : None,
                "error" : {
                    "code" : 6001,
                    "message" : "단어와 블록의 개수가 일치하지 않습니다."
                },
                "success": False
            })
        result = gemini_preview(serializer.data['sentence'], serializer.data['word'])
        return Response({
            "responseDto": {
                "result": result
            },
            "error": None,
            "success": True
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)