from .serializers import (
    PromptSerializer,
    PreviewSerializer,
    EvalSerializer
)
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .utils import (
    llm_preview,
    llm_pdf,
    find_payload,
    fallback_response,
    get_history_tuple,
    llm_answer_his
)
from .eval import prompt_eval, get_chat_data
from .models import prompt_tb
from .template import korean_template
from users.models import user_tb, chatroom_tb
from .multimodal.image import llm_answer_his_img
from .multimodal.pdf import llm_answer_his_pdf
from config.settings.base import JWT_SECRET_KEY

@api_view(['POST'])
def create_question(request):
    serializer = PromptSerializer(data=request.data)
    token = request.headers.get('Authorization')
    language = request.headers.get('Accept-Language')
    if token is None:
        return Response({
            "error": 4046,
            "success": False
        })
    if serializer.is_valid():
        promptId = serializer.data['promptId']
        token_id = find_payload(token, JWT_SECRET_KEY)['id']
        user = user_tb.objects.get(social_id=token_id)
        try:
            if promptId is not None:
                prompt = prompt_tb.objects.get(pk=promptId)
                if prompt.user != user:
                    return Response({
                        "error": 4039,
                        "success": False
                    })
                prompt = prompt.prompt_preview
            else:
                prompt = ""
            if language == "ko":
                prompt += korean_template
            messageQuestion = serializer.data['messageQuestion']
            messageFile = serializer.data['messageFile']
            fileType = serializer.data['fileType']
            chatroomId = serializer.data['chatroomId']
            try:
                chatroom = chatroom_tb.objects.get(pk=chatroomId)
            except chatroom_tb.DoesNotExist:
                return Response({
                    "error": 4044,
                    "success": False
                })
            if chatroom.user != user:
                return Response({
                    "error": 40310,
                    "success": False
                })
            history = get_history_tuple(chatroomId)
            # history = get_history(chatroomId)
            if fileType == "image":
                answer = llm_answer_his_img(prompt, messageQuestion, history, messageFile)
                # answer = llm_img(prompt, messageQuestion, messageFile, history)
            elif fileType == "pdf":
                answer = llm_answer_his_pdf(prompt, messageQuestion, messageFile, history)
                # answer = llm_pdf(prompt, messageQuestion, messageFile, history)
            else:
                #answer = llm_answer(prompt, messageQuestion, history)
                answer = llm_answer_his(prompt, messageQuestion, history)
            if len(answer) < 3:
                answer = fallback_response(language)
            # data = {
            #         "prompt": promptId,
            #         "message_answer": answer["response"],
            #         "message_file": messageFile,
            #         "message_question": messageQuestion,
            #         "chatroom": chatroomId,
            #         }
            # message_serializer = MessageSerializer(data=data)
            # message_serializer.is_valid(raise_exception=True)
            # message_serializer.save()
            return Response({
                "responseDto": {
                    "messageAnswer": answer,
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
def prompt_evaluation(request):
    serializer = EvalSerializer(data=request.data)
    # token = request.headers.get('Authorization')
    # language = request.headers.get('Accept-Language')
    # if token is None:
    #     return Response({
    #         "error": 4046,
    #         "success": False
    #     })
    if serializer.is_valid():
        promptId = serializer.data['promptId']
        # token_id = find_payload(token, JWT_SECRET_KEY)['id']
        # user = user_tb.objects.get(social_id=token_id)
        try:
            if promptId is not None:
                prompt = prompt_tb.objects.get(pk=promptId)
                # if prompt.user != user:
                #     return Response({
                #         "error": 4039,
                #         "success": False
                #     })
                prompt = prompt.prompt_preview
                chat_data = get_chat_data(promptId)
                if (len(chat_data) < 5):
                    return Response({
                        "error": 40311,
                        "success": False
                    })
                result = prompt_eval(prompt, chat_data)
            else:
                return Response({
                    "error": 4039,
                    "success": False
                })
        except prompt_tb.DoesNotExist:
            return Response({
                "error":4043,
                "success": False
            })
    return Response({
        "responseDto": {
            "promptEvaluation": result,
            # "prompt": prompt,
            "chat_data": chat_data,
        },
        "error": None,
        "success": True
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_preview(request):
    serializer = PreviewSerializer(data=request.data)
    if serializer.is_valid():
        if (len(serializer.data['blockCategory']) != len(serializer.data['blockDescription'])):
            return Response({
                "responseDto": None,
                "error": {
                    "code": 6001,
                    "message": "단어와 블록의 개수가 일치하지 않습니다."
                },
                "success": False
            })
        result = llm_preview(serializer.data['blockCategory'], serializer.data['blockDescription'])
        return Response({
            "responseDto": {
                "result": result
            },
            "error": None,
            "success": True
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)