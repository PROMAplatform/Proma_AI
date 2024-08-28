from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import QuestionSerializer, ChatroomSerilaizer, MessageSerializer
from llm.utils import find_payload, get_history, gemini_answer
from llm.models import prompt_tb
from users.models import user_tb, chatroom_tb
# Create your views here.

@api_view(['POST'])
def api_question(request):
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.data['apiToken']
        key = serializer.data['secretKey']
        messageQuestion = serializer.data['messageQuestion']
        userLoginId = serializer.data['userLoginId']
        payload = find_payload(token, key)
        user = user_tb.objects.get(social_id=payload['id'])
        try:
            chatroom = chatroom_tb.objects.get(chat_room_title=userLoginId)
            if chatroom.user.id != user.id:
                data = {
                    "chat_room_title": userLoginId,
                    "emoji": "💡",
                    "user": user.id
                }
                chatroom_serializer = ChatroomSerilaizer(data=data)
                chatroom_serializer.is_valid(raise_exception=True)
                chatroom = chatroom_serializer.save()
        except chatroom_tb.DoesNotExist:
            data = {
                "chat_room_title": userLoginId,
                "emoji": "💡",
                "user": user.id
            }
            chatroom_serializer = ChatroomSerilaizer(data=data)
            chatroom_serializer.is_valid(raise_exception=True)
            chatroom = chatroom_serializer.save()
        prompt = prompt_tb.objects.get(pk=payload['promptId']).prompt_preview
        history = get_history(chatroom.id)
        answer = gemini_answer(prompt, messageQuestion, history)
        data = {
            "prompt": payload['promptId'],
            "message_answer": answer,
            "message_file": "",
            "message_question": messageQuestion,
            "chatroom": chatroom.id,
        }
        message_serializer = MessageSerializer(data=data)
        message_serializer.is_valid(raise_exception=True)
        message_serializer.save()
        return Response({
            "responseDto": {
                "messageAnswer": answer,
            },
            "success": True,
            "error": None
        }, status=status.HTTP_200_OK)