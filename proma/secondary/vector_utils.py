import numpy as np
from transformers import pipeline
from sklearn.decomposition import PCA
from collections import defaultdict
from .models import block_history_log_embed_tb, block_history_log_pca_tb
import json

# ----------------- 임베딩 및 벡터 매핑 관련 함수 -----------------
def get_all_keywords(db_records, user_record, fields):
    keywords_set = set()
    for record in db_records + [user_record]:
        for field in fields:
            value = record.get(field)
            if value and value.strip():
                keywords_set.add(value)
    return list(keywords_set)

def create_embedding_pipeline(model_name="nlpai-lab/KoE5"):
    return pipeline("feature-extraction", model=model_name, tokenizer=model_name)

def get_embedding(keyword, feature_extractor):
    output = feature_extractor(keyword, truncation=True)
    embedding = np.mean(output[0], axis=0)
    return embedding

def compute_keyword_embeddings(keywords, feature_extractor):
    return {kw: get_embedding(kw, feature_extractor) for kw in keywords if kw and kw.strip()}

def compute_pca_transform(embeddings_matrix, n_components=3):
    pca = PCA(n_components=n_components)
    transformed = pca.fit_transform(embeddings_matrix)
    return pca, transformed

def keyword_to_vector(keyword, keyword_embeddings, pca):
    if keyword not in keyword_embeddings:
        raise KeyError(f"Keyword '{keyword}' not found in embeddings")
    emb = keyword_embeddings[keyword]
    return pca.transform([emb])[0]

def create_keyword_to_vector_func(keyword_embeddings, pca):
    return lambda kw: keyword_to_vector(kw, keyword_embeddings, pca) if kw and kw.strip() else None

def record_to_vector(record, fields, keyword_to_vector_func):
    return {field: keyword_to_vector_func(record.get(field)) for field in fields}

# ----------------- DB 관련 함수 -----------------
def save_to_embed_tb(keyword_embeddings):
    # 기존 임베딩 삭제
    block_history_log_embed_tb.objects.all().delete()
    
    # 새 임베딩 저장
    for keyword, embedding in keyword_embeddings.items():
        # numpy array를 리스트로 변환하여 저장
        block_history_log_embed_tb.objects.create(
            keyword=embedding.tolist() if hasattr(embedding, 'tolist') else embedding
        )

def save_to_pca_tb(record, vector_record):
    # 벡터와 원본 값을 함께 저장
    block_history_log_pca_tb.objects.create(
        v_type=vector_record.get('타입', [0, 0, 0]).tolist() if hasattr(vector_record.get('타입', [0, 0, 0]), 'tolist') else vector_record.get('타입', [0, 0, 0]),
        v_category=vector_record.get('카테고리', [0, 0, 0]).tolist() if hasattr(vector_record.get('카테고리', [0, 0, 0]), 'tolist') else vector_record.get('카테고리', [0, 0, 0]),
        v_speaker=vector_record.get('화자', [0, 0, 0]).tolist() if hasattr(vector_record.get('화자', [0, 0, 0]), 'tolist') else vector_record.get('화자', [0, 0, 0]),
        v_listener=vector_record.get('청자', [0, 0, 0]).tolist() if hasattr(vector_record.get('청자', [0, 0, 0]), 'tolist') else vector_record.get('청자', [0, 0, 0]),
        v_instruction=vector_record.get('지시', [0, 0, 0]).tolist() if hasattr(vector_record.get('지시', [0, 0, 0]), 'tolist') else vector_record.get('지시', [0, 0, 0]),
        v_form=vector_record.get('형식', [0, 0, 0]).tolist() if hasattr(vector_record.get('형식', [0, 0, 0]), 'tolist') else vector_record.get('형식', [0, 0, 0]),
        v_excluded=vector_record.get('제외', [0, 0, 0]).tolist() if hasattr(vector_record.get('제외', [0, 0, 0]), 'tolist') else vector_record.get('제외', [0, 0, 0]),
        v_required=vector_record.get('필수', [0, 0, 0]).tolist() if hasattr(vector_record.get('필수', [0, 0, 0]), 'tolist') else vector_record.get('필수', [0, 0, 0]),
        o_type=record.get('타입', ''),
        o_category=record.get('카테고리', ''),
        o_speaker=record.get('화자', ''),
        o_listener=record.get('청자', ''),
        o_instruction=record.get('지시', ''),
        o_form=record.get('형식', ''),
        o_excluded=record.get('제외', ''),
        o_required=record.get('필수', '')
    )

def load_from_embed_tb():
    embeddings = block_history_log_embed_tb.objects.all()
    if not embeddings.exists():
        return None
    
    keyword_embeddings = {}
    for embed in embeddings:
        # VectorField에서 가져온 값을 numpy 배열로 변환
        keyword_embeddings[str(embed.id)] = np.array(embed.keyword)
    return keyword_embeddings

def load_from_pca_tb():
    records = block_history_log_pca_tb.objects.all()
    if not records.exists():
        return [], []
    
    db_records = []
    db_vector_records = []
    
    for record in records:
        # 원본 레코드 구성
        original_record = {
            '타입': record.o_type,
            '카테고리': record.o_category,
            '화자': record.o_speaker,
            '청자': record.o_listener,
            '지시': record.o_instruction,
            '형식': record.o_form,
            '제외': record.o_excluded,
            '필수': record.o_required
        }
        
        # 벡터 레코드 구성 - VectorField에서 가져온 값을 numpy 배열로 변환
        vector_record = {
            '타입': np.array(record.v_type),
            '카테고리': np.array(record.v_category),
            '화자': np.array(record.v_speaker),
            '청자': np.array(record.v_listener),
            '지시': np.array(record.v_instruction),
            '형식': np.array(record.v_form),
            '제외': np.array(record.v_excluded),
            '필수': np.array(record.v_required)
        }
        
        db_records.append(original_record)
        db_vector_records.append(vector_record)
    
    return db_records, db_vector_records

# ----------------- 유사도 비교 관련 함수 -----------------
def compute_similarity(user_vector, db_vector, fields):
    distances = []
    for field in fields:
        if user_vector.get(field) is not None and db_vector.get(field) is not None:
            # 벡터를 numpy 배열로 변환
            user_vec = np.array(user_vector[field]) if not isinstance(user_vector[field], np.ndarray) else user_vector[field]
            db_vec = np.array(db_vector[field]) if not isinstance(db_vector[field], np.ndarray) else db_vector[field]
            
            # 벡터가 1차원이 아닌 경우 1차원으로 변환
            if user_vec.ndim > 1:
                user_vec = user_vec.flatten()
            if db_vec.ndim > 1:
                db_vec = db_vec.flatten()
                
            d = float(np.linalg.norm(user_vec - db_vec))
            distances.append(d)
    return float(np.mean(distances)) if distances else float('inf')

def get_top_similar_records(user_vector_record, db_vector_records, fields, top_n=5):
    similarity_scores = [(idx, compute_similarity(user_vector_record, db_vector, fields)) 
                         for idx, db_vector in enumerate(db_vector_records)]
    similarity_scores.sort(key=lambda x: x[1])
    top_indices = [idx for idx, dist in similarity_scores[:top_n]]
    return top_indices, similarity_scores[:top_n]

# ----------------- 추천 관련 함수 -----------------
def recommend_keywords(user_record, top_records, fields):
    recommendations = {}
    excluded_fields = ["타입", "카테고리"]
    
    for field in fields:
        if field not in excluded_fields:  # 타입과 카테고리를 제외한 모든 필드에 대해 추천
            freq = defaultdict(int)
            for record in top_records:
                if record.get(field):
                    freq[record[field]] += 1
            
            # 사용자의 현재 키워드를 제외하고 정렬
            current_keyword = user_record.get(field, '')
            sorted_candidates = sorted(
                [(kw, count) for kw, count in freq.items() if kw != current_keyword],
                key=lambda x: x[1],
                reverse=True
            )
            
            if sorted_candidates:
                recommendations[field] = [kw for kw, count in sorted_candidates]
            else:
                recommendations[field] = []
    
    return recommendations

# ----------------- 전체 실행 함수 -----------------
def process_user_record(user_record, update_db=True):
    fields = ["타입", "카테고리", "화자", "청자", "지시", "형식", "제외", "필수"]
    
    try:
        # 1. 기존 DB와 벡터 DB 로드
        db_records, db_vector_records = load_from_pca_tb()
        keyword_embeddings = load_from_embed_tb()
        
        # 2. 벡터 DB가 없거나 임베딩이 없는 경우 초기화
        if not db_vector_records or not keyword_embeddings:
            all_keywords = get_all_keywords(db_records or [], user_record, fields)
            feature_extractor = create_embedding_pipeline()
            keyword_embeddings = compute_keyword_embeddings(all_keywords, feature_extractor)
            embeddings_matrix = np.array(list(keyword_embeddings.values()))
            pca, _ = compute_pca_transform(embeddings_matrix)
            keyword_to_vector_func = create_keyword_to_vector_func(keyword_embeddings, pca)
            db_vector_records = [record_to_vector(record, fields, keyword_to_vector_func) 
                               for record in (db_records or [])]
            save_to_embed_tb(keyword_embeddings)
            
            # 기존 레코드가 있다면 PCA 테이블에 저장
            if db_records:
                for record, vector_record in zip(db_records, db_vector_records):
                    save_to_pca_tb(record, vector_record)
        
        # 3. 사용자 기록 벡터화
        keyword_to_vector_func = create_keyword_to_vector_func(keyword_embeddings, pca)
        user_vector_record = record_to_vector(user_record, fields, keyword_to_vector_func)
        
        # 4. 임시로 사용자 기록을 DB에 추가
        if update_db:
            # numpy array를 list로 변환하여 저장
            vector_record_for_db = {}
            for field in fields:
                vec = user_vector_record.get(field)
                if vec is not None:
                    if isinstance(vec, np.ndarray):
                        vector_record_for_db[field] = vec.tolist()
                    else:
                        vector_record_for_db[field] = list(vec)
                else:
                    vector_record_for_db[field] = [0, 0, 0]
            
            save_to_pca_tb(user_record, vector_record_for_db)
            
        # 5. 업데이트된 DB 다시 로드
        db_records, db_vector_records = load_from_pca_tb()
        
        # 6. 유사도 계산
        top_indices, similarity_scores = get_top_similar_records(user_vector_record, db_vector_records, fields)
        top_similar_records = [db_records[idx] for idx in top_indices]
        
        # 7. 추천 후보 키워드 추출
        recommendations = recommend_keywords(user_record, top_similar_records, fields)
        
        # 8. 사용자 기록 삭제
        if update_db:
            # 가장 최근에 추가된 레코드 삭제 (사용자 기록)
            latest_record = block_history_log_pca_tb.objects.latest('id')
            latest_record.delete()
        
        # 9. 결과 반환
        return {
            'similar_records': [
                {
                    'record': record,
                    'distance': float(dist)  # numpy.float64를 파이썬 float로 변환
                }
                for record, (_, dist) in zip(top_similar_records, similarity_scores)
            ],
            'recommendations': recommendations
        }
    except Exception as e:
        print(f"Error in process_user_record: {str(e)}")
        raise 