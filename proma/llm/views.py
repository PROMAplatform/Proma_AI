from django.shortcuts import render
from .serializers import PromptSerializer, PreviewSerializer, MessageSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .utils import gemini_answer, gemini_preview, chat_img, get_history, gemini_img
from .models import prompt_tb
from datetime import datetime

@api_view(['POST'])
def create_question(request):
    serializer = PromptSerializer(data=request.data)
    if serializer.is_valid():
        promptId = serializer.data['promptId']
        try:
            if(promptId is not None):
                prompt = prompt_tb.objects.get(pk=promptId).prompt_preview
            else:
                prompt = ""
            messageQuestion = serializer.data['messageQuestion']
            messageFile = serializer.data['messageFile']
            fileType = serializer.data['fileType']
            chatroomId = serializer.data['chatroomId']
            history = get_history(chatroomId)
            if fileType == "image":
                answer = gemini_img(prompt, messageQuestion, messageFile, history) #chat_img(prompt, messageQuestion, messageFile, history)
            else:
                answer = gemini_answer(prompt, messageQuestion, messageFile, history)
            data = {"prompt":promptId,
                    "message_answer": answer,
                    "message_file":messageFile,
                    "message_question":messageQuestion,
                    "chatroom":chatroomId,
                    }
            message_serializer = MessageSerializer(data=data)
            message_serializer.is_valid(raise_exception=True)
            message_serializer.save()
            return Response({
                "responseDto": {
                    "messageAnswer": answer
                },
                "error":None,
                "success": True
            },status=status.HTTP_200_OK)
        except prompt_tb.DoesNotExist:
            return Response({
                "error":4043,
                "success": False
            })
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