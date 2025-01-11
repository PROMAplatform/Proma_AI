from django.shortcuts import render
from rest_framework.decorators import api_view
from config.settings.base import JWT_SECRET_LIGENT_KEY
from rest_framework.response import Response
from rest_framework import status
from .models import (
    room_tb,
    keyword_tb,
    category_tb,
    character_tb,
    personalities_tb
)
from .serializers import (
    IntroduceSerializer,
    RoomChatSerializer,
    InterviewSerializer,
    RoomInterviewSerializer
)
from .agent import Agent
from .utils import get_dialogue, get_history


# Create your views here.
@api_view(['POST'])
def generate_introduce(request):
    serializer = IntroduceSerializer(data=request.data)
    token = request.headers.get('Authorization')
    if serializer.is_valid():
      room_id = serializer.data['roomId']
      character_id = serializer.data['characterId']
      room = room_tb.objects.get(pk=room_id)
      keyword =keyword_tb.objects.get(pk=room.keyword.id)
      category = category_tb.objects.get(pk=keyword.category.id)
      character = character_tb.objects.get(pk=character_id)
      personality = personalities_tb.objects.get(character_id=character_id)
      if character_id == room.liar_character_id:
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
          },
          "error": None,
          "success": True
      }, status=status.HTTP_200_OK)

@api_view(['POST'])
def generate_interview(request):
    serializer = InterviewSerializer(data=request.data)
    token = request.headers.get('Authorization')
    if serializer.is_valid():
        room_id = serializer.data['roomId']
        character_id = serializer.data['characterId']
        question = serializer.data['question']
        room = room_tb.objects.get(pk=room_id)
        keyword = keyword_tb.objects.get(pk=room.keyword.id)
        category = category_tb.objects.get(pk=keyword.category.id)
        character = character_tb.objects.get(pk=character_id)
        personality = personalities_tb.objects.get(character_id=character_id)
        if character_id == room.liar_character_id:
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

