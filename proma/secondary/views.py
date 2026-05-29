from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import llm.utils
from llm.evalues2 import evaluate_rag_simple
from llm.multimodal.evalues3 import evaluate_rag_simple_bert
from llm.multimodal.evalus import evaluate_rag_performance
from llm.multimodal.recommendRag import llm_answer_block_history_rag, get_o_fields_list
from .models import block_history_log_pca_tb
from .vector_utils import process_user_record, compute_keyword_embeddings, create_embedding_pipeline, compute_pca_transform, save_to_pca_tb
from .serializers import (
    BlockRecommendRequestSerializer,
    BlockRecommendResponseSerializer
)
import numpy as np
from langchain_core.documents import Document
from datetime import datetime
from collections import namedtuple
from .vector_utils_2 import process_user_record_anyway2


@api_view(['POST'])
def rag_block_recommend(request):
    try:
        request_serializer = BlockRecommendRequestSerializer(data=request.data)
        category = BlockRecommendRequestSerializer(data=request.data.get('category'))
        method = BlockRecommendResponseSerializer(data=request.data.get('type'))

        if not request_serializer.is_valid():
            return Response(
                {"status": "error", "message": request_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        # else:
        #     user_inputs = request_serializer.validated_data
        #     answer = llm_answer_block_history_rag(
        #         str(method), str(category), language, user_inputs,
        #     )

        fields = ["speaker", "listener", "instruction", "form", "excluded", "required"]

        answer = llm_answer_block_history_rag(str(method), str(category), "ko", request_serializer.validated_data)

        print(answer)

        data = json.loads(answer)

        Document1 = namedtuple('Document', ['page_content'])
        history= []

        if isinstance(data, dict):
            # 딕셔너리 구조: {"blockCategory": [...], "blockValue": [...]}
            block_categories = data.get('blockCategory', [])
            block_values = data.get('blockValue', [])
            for key, value in zip(block_categories, block_values):
                doc = Document1(page_content=f"o_{key}:{value}")
                history.append(doc)
        elif isinstance(data, list):
            # 리스트 구조: [{"blockCategory": ..., "blockValue": ...}, ...]
            for item in data:
                block_category = item.get('blockCategory')
                block_value = item.get('blockValue')
                doc = Document1(page_content=f"o_{block_category}:{block_value}")
                history.append(doc)
        else:
            raise ValueError("answer의 JSON 구조를 확인하세요.")

        print(history)

        query_fields = {
            k: v for k, v in request_serializer.validated_data.items()
            if k not in ['type', 'category'] and v.strip()
        }

        evaluate_rag_simple_bert(query_fields, history)


        formatted_data = [
            {
                "blockCategory": item['blockCategory'],
                "blockValue": item['blockValue'],
                "blockDescription": item['blockDescription']
            }
            for item in data
        ]

        return Response({
            "responseDto": {
                'selectBlock': formatted_data
            }
        })

    except Exception as e:
        print(f"Error in block_recommend: {str(e)}")  # 디버깅용 로그
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



# Create your views here.

@api_view(['POST'])
def block_recommend(request):
    try:
        # 요청 데이터 검증
        request_serializer = BlockRecommendRequestSerializer(data=request.data)
        category = BlockRecommendRequestSerializer(data=request.data.get('category'))
        if not request_serializer.is_valid():
            return Response(
                {"status": "error", "message": request_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 유사도 계산 및 추천
        result = process_user_record(request_serializer.validated_data, update_db=True)
        
        # recommendations에서 타입과 카테고리를 제외
        all_recommendations = {
            field: values
            for field, values in result["recommendations"].items()
            if field not in ["type", "category"]
        }

        history = []
        for key, values in all_recommendations.items():
            for value in values:
                doc = Document(
                    page_content=f"o_{key}:{value}"
                )
                history.append(doc)
        print(history)
        print("asdlkfjasdlkfjasklfjalskfjlksa")
        history2 = []
        for key, value in all_recommendations.items():
            history2.append({"type": f"{key}: {value}"})

        print("\n" + "🔍 벡터 검색 결과 평가 시작" + "\n")
        query_fields = {
            k: v for k, v in request_serializer.validated_data.items()
            if k not in ['type', 'category'] and v.strip()
        }

        evaluation_results = evaluate_rag_simple_bert(query_fields, history)

        answer = llm.utils.llm_answer_block_history("task/research", str(category), history2, "ko")

        #print(answer)
        data = json.loads(answer)

        Document1 = namedtuple('Document', ['page_content'])

        Document1 = namedtuple('Document', ['page_content'])
        history= []

        if isinstance(data, dict):
            # 딕셔너리 구조: {"blockCategory": [...], "blockValue": [...]}
            block_categories = data.get('blockCategory', [])
            block_values = data.get('blockValue', [])
            for key, value in zip(block_categories, block_values):
                doc = Document1(page_content=f"o_{key}:{value}")
                history.append(doc)
        elif isinstance(data, list):
            # 리스트 구조: [{"blockCategory": ..., "blockValue": ...}, ...]
            for item in data:
                block_category = item.get('blockCategory')
                block_value = item.get('blockValue')
                doc = Document1(page_content=f"o_{block_category}:{block_value}")
                history.append(doc)
        else:
            raise ValueError("answer의 JSON 구조를 확인하세요.")

        print(history)
        evaluate_rag_simple_bert(query_fields, history)

        formatted_data = [
            {
                "blockCategory": item['blockCategory'],
                "blockValue": item['blockValue'],
                "blockDescription": item['blockDescription']
            }
            for item in data
        ]


        return Response({
            "responseDto": {
                'selectBlock': formatted_data
            }
        })

    except Exception as e:
        print(f"Error in block_recommend: {str(e)}")  # 디버깅용 로그
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def save_block(request):
    try:
        # 요청 데이터 검증
        request_serializer = BlockRecommendRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                {"status": "error", "message": request_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_record = request_serializer.validated_data
        fields = ["type", "category", "speaker", "listener", "instruction", "form", "excluded", "required"]

        # 키워드 추출
        keywords = set()
        for field in fields:
            if user_record.get(field):
                keywords.add(user_record[field])
        
        if not keywords:
            return Response(
                {"status": "error", "message": "No valid keywords found in the request"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 임베딩 생성
        feature_extractor = create_embedding_pipeline()
        keyword_embeddings = compute_keyword_embeddings(list(keywords), feature_extractor)
        
        if not keyword_embeddings:
            return Response(
                {"status": "error", "message": "Failed to generate embeddings"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # PCA 변환을 위한 임베딩 매트릭스 생성
        embeddings_matrix = np.array(list(keyword_embeddings.values()))
        pca, _ = compute_pca_transform(embeddings_matrix)
        
        # 벡터 생성
        vector_record = {}
        for field in fields:
            if user_record.get(field) and user_record[field] in keyword_embeddings:
                # 해당 키워드의 임베딩을 PCA로 변환
                embedding = keyword_embeddings[user_record[field]]
                vector = pca.transform([embedding])[0]
                vector_record[field] = vector.tolist()
            else:
                vector_record[field] = [0, 0, 0]
        
        # PCA DB에만 저장
        try:
            save_to_pca_tb(user_record, vector_record)
            
            return Response({
                "status": "success",
                "message": "Block saved successfully"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Failed to save to database: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        print(f"Error in save_block: {str(e)}")  # 디버깅용 로그
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def parse_blocks(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    result = []
    current_category = None
    i = 0
    while i < len(lines):
        line = lines[i]
        # 카테고리(블록)명일 경우
        if not line.startswith('Title:') and not line.startswith('Description:'):
            current_category = line
            i += 1
            continue
        # Title/Description 쌍 파싱
        if line.startswith('Title:'):
            title = line.replace('Title:', '').strip()
            # 다음 줄이 Description인지 확인
            if i+1 < len(lines) and lines[i+1].startswith('Description:'):
                description = lines[i+1].replace('Description:', '').strip()
                result.append({
                    "blockCategory": current_category,
                    "blockValue": title,
                    "blockDescription": description
                })
                i += 2
                continue
        i += 1
    return result