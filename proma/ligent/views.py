from django.shortcuts import render
from rest_framework.decorators import api_view
from config.settings.base import JWT_SECRET_LIGENT_KEY
from rest_framework.response import Response
from rest_framework import status
import uuid
from .error import *
from .models import (
    room_tb,
    keyword_tb,
    category_tb,
    character_tb,
    personalities_tb,
    room_chat_tb,
    user_tb
)
from .serializers import (
    IntroduceSerializer,
    RoomChatSerializer,
    InterviewSerializer,
    RoomInterviewSerializer
)
from .agent import Agent
from .utils import get_dialogue, get_history, find_payload

# Create your views here.
@api_view(['POST'])
def generate_introduce(request):
    serializer = IntroduceSerializer(data=request.data)
    token = request.headers.get('Authorization')
    if token is None:
        return Response({
            "error": TOKEN_MALFORMED_ERROR,
            "success": False,
        }, status=status.HTTP_401_UNAUTHORIZED)
    if serializer.is_valid():
        token_id = find_payload(token, JWT_SECRET_LIGENT_KEY)['uid']
        room_id = serializer.data['roomId']
        character_id = serializer.data['characterId']
        if room_chat_tb.objects.filter(room=room_id, character=character_id).exists():
              return Response({
                  "error": ALREADY_ANSWER,
                  "success": False,
              }, status=status.HTTP_403_FORBIDDEN)
        room = room_tb.objects.get(pk=room_id)
        keyword =keyword_tb.objects.get(pk=room.keyword.id)
        category = category_tb.objects.get(pk=keyword.category.id)
        character = character_tb.objects.get(pk=character_id)
        personality = personalities_tb.objects.get(character=character_id)
        if character_id == room.liar_character.id:
            is_liar = True
        else:
            is_liar = False
        agent = Agent(
            personality=personality,
            agent_name=character.name,
            category=category.name,
            word=keyword.name,
            explain_sen=keyword.description,
            is_liar=is_liar
        )
        dialogue = get_dialogue(room)
        answer = agent.introduce(dialogue)
        data = {
            "chat_content": answer,
            "character": character_id,
            "room": room_id
        }
        room_chat_serializer = RoomChatSerializer(data=data)
        room_chat_serializer.is_valid(raise_exception=True)
        room_chat_serializer.save()
        return Response({
            "responseDto": {
                "chatContent": answer,
                "liar": room.liar_character.id,
            },
            "error": None,
            "success": True
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
def generate_interview(request):
    serializer = InterviewSerializer(data=request.data)
    token = request.headers.get('Authorization')
    if token is None:
        return Response({
            "error": TOKEN_MALFORMED_ERROR,
            "success": False,
        }, status=status.HTTP_401_UNAUTHORIZED)
    if serializer.is_valid():
        token_id = find_payload(token, JWT_SECRET_LIGENT_KEY)['uid']
        room_id = serializer.data['roomId']
        character_id = serializer.data['characterId']
        question = serializer.data['question']
        room = room_tb.objects.get(pk=room_id)
        if (room.question_count is None or room.question_count < 1):
            return Response({
                "error": LAKE_OF_INTERVIEW_CHANCE,
                "success": False,
            }, status=status.HTTP_403_FORBIDDEN)
        keyword = keyword_tb.objects.get(pk=room.keyword.id)
        category = category_tb.objects.get(pk=keyword.category.id)
        character = character_tb.objects.get(pk=character_id)
        personality = personalities_tb.objects.get(character_id=character_id)
        if character_id == room.liar_character.id:
            is_liar = True
        else:
            is_liar = False
        agent = Agent(
            personality=personality,
            agent_name=character.name,
            category=category.name,
            word=keyword.name,
            explain_sen=keyword.description,
            is_liar=is_liar
        )
        dialogue = get_dialogue(room)
        history = get_history(room_id, character_id)
        answer = agent.interview(question, dialogue, history)
        data = {
            "question": question,
            "answer": answer,
            "room": room_id,
            "character": character_id
        }
        room.question_count -= 1
        room.save()
        room_interview_serializer = RoomInterviewSerializer(data=data)
        room_interview_serializer.is_valid(raise_exception=True)
        room_interview_serializer.save()
        return Response({
            "responseDto": {
                "answer": answer,
            },
            "error": None,
            "success": True
        }, status=status.HTTP_200_OK)

