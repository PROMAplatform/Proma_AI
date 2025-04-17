from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .vector_utils import process_user_record, compute_keyword_embeddings, create_embedding_pipeline, compute_pca_transform, save_to_pca_tb
from .serializers import (
    BlockRecommendRequestSerializer,
    BlockRecommendResponseSerializer
)
import numpy as np

# Create your views here.

@api_view(['POST'])
def block_recommend(request):
    try:
        # 요청 데이터 검증
        request_serializer = BlockRecommendRequestSerializer(data=request.data)
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
            if field not in ["타입", "카테고리"]
        }
        
        # 응답 데이터 구성
        response_data = {
            "status": "success",
            "similar_records": [
                {
                    "record": {
                        field: str(value) if value is not None else ''
                        for field, value in record.items()
                    },
                    "similarity_score": float(1 - dist)  # 거리를 유사도 점수로 변환 (0~1 사이)
                }
                for record, dist in zip(
                    [r["record"] for r in result["similar_records"]], 
                    [r["distance"] for r in result["similar_records"]]
                )
            ],
            "recommendations": all_recommendations  # 딕셔너리 형태 유지
        }
        
        # 응답 데이터 검증
        response_serializer = BlockRecommendResponseSerializer(data=response_data)
        if not response_serializer.is_valid():
            print(f"Serializer errors: {response_serializer.errors}")  # 디버깅용 로그
            return Response(
                {
                    "status": "error", 
                    "message": "Invalid response format",
                    "details": response_serializer.errors
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
        
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
        fields = ["타입", "카테고리", "화자", "청자", "지시", "형식", "제외", "필수"]
        
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
