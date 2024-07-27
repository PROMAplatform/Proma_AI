from django.shortcuts import render
from .serializers import PromptSerializer, PreviewSerializer, ChatbotSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .utils import gemini_answer, gemini_preview, openai_preview, dgu_chatbot

'''
create_question 예제 데이터
{
  "pdf": "",
  "prompt": "너는 엔지니어야. 일반인의 수준에서 이해할 수 있게 설명해줘. 문서 써줘. 쉬운 예시의 형식으로 설명해줘. 장점과 단점은 꼭 들어가도록 설명해줘. 부정적인 표현은 제외하고 설명해줘.",
  "question": "프롬프트 엔지니어링은 뭐가 좋아?"
}
'''
@api_view(['POST'])
def create_question(request):
    serializer = PromptSerializer(data=request.data)
    if serializer.is_valid():
        answer = gemini_answer(serializer.data['prompt'],
                               serializer.data['question'],
                               serializer.data['pdf'])
        return Response({
            "responseDto" : {
                "answer": answer
            },
            "error":None,
            "success": True
        },status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def dgu_question(request):
    serializer = ChatbotSerializer(data=request.data)
    if serializer.is_valid():
        answer = dgu_chatbot(serializer.data['question'])
        return Response({
            "responseDto" : {
                "answer": answer
            },
            "error":None,
            "success": True
        },status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


'''
create_preview 예제 데이터
{
  "sentence":["너는 __이야.","__의 수준에서 이해할 수 있게 설명해줘.", "__를 해줘.", "__의 형식으로 설명해줘.", "__는 꼭 들어가도록 설명해줘.", "__는 제외하고 설명해줘."],
  "word":["엔지니어", "일반인", "문서 작성", "쉬운 예시", "장점과 단점", "부정적인 표현"]
}
'''
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