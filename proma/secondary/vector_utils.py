import numpy as np
from transformers import pipeline
from sklearn.decomposition import PCA
from collections import defaultdict
from .models import block_history_log_embed_tb, block_history_log_pca_tb
import json
from datetime import datetime


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


def compute_keyword_embeddings(keywords, feature_extractor, existing_embeddings=None):
    if existing_embeddings is None:
        existing_embeddings = {}

    # 새로운 키워드에 대해서만 임베딩 계산
    new_embeddings = {}
    for kw in keywords:
        if kw and kw.strip():
            if kw in existing_embeddings:
                new_embeddings[kw] = existing_embeddings[kw]
            else:
                new_embeddings[kw] = get_embedding(kw, feature_extractor)

    return new_embeddings


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
    # 각 키워드에 대해 개별적으로 처리
    for keyword, embedding in keyword_embeddings.items():
        # 기존 임베딩이 있는지 확인
        existing_embed = block_history_log_embed_tb.objects.filter(o_keyword=keyword).first()

        if existing_embed:
            # 기존 임베딩 업데이트
            existing_embed.keyword = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            existing_embed.save()
        else:
            # 새 임베딩 생성
            block_history_log_embed_tb.objects.create(
                o_keyword=keyword,
                keyword=embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            )


def save_to_pca_tb(record, vector_record):
    # 벡터와 원본 값을 함께 저장
    block_history_log_pca_tb.objects.create(
        v_type=vector_record.get('type', [0, 0, 0]).tolist() if hasattr(vector_record.get('type', [0, 0, 0]),
                                                                        'tolist') else vector_record.get('type',
                                                                                                         [0, 0, 0]),
        v_category=vector_record.get('category', [0, 0, 0]).tolist() if hasattr(
            vector_record.get('category', [0, 0, 0]), 'tolist') else vector_record.get('category', [0, 0, 0]),
        v_speaker=vector_record.get('speaker', [0, 0, 0]).tolist() if hasattr(vector_record.get('speaker', [0, 0, 0]),
                                                                              'tolist') else vector_record.get(
            'speaker', [0, 0, 0]),
        v_listener=vector_record.get('listener', [0, 0, 0]).tolist() if hasattr(
            vector_record.get('listener', [0, 0, 0]), 'tolist') else vector_record.get('listener', [0, 0, 0]),
        v_instruction=vector_record.get('instruction', [0, 0, 0]).tolist() if hasattr(
            vector_record.get('Instruction', [0, 0, 0]), 'tolist') else vector_record.get('Instruction', [0, 0, 0]),
        v_form=vector_record.get('form', [0, 0, 0]).tolist() if hasattr(vector_record.get('form', [0, 0, 0]),
                                                                        'tolist') else vector_record.get('form',
                                                                                                         [0, 0, 0]),
        v_excluded=vector_record.get('excluded', [0, 0, 0]).tolist() if hasattr(
            vector_record.get('excluded', [0, 0, 0]), 'tolist') else vector_record.get('excluded', [0, 0, 0]),
        v_required=vector_record.get('required', [0, 0, 0]).tolist() if hasattr(
            vector_record.get('required', [0, 0, 0]), 'tolist') else vector_record.get('required', [0, 0, 0]),
        o_type=record.get('type', ''),
        o_category=record.get('category', ''),
        o_speaker=record.get('speaker', ''),
        o_listener=record.get('listener', ''),
        o_instruction=record.get('Instruction', ''),
        o_form=record.get('form', ''),
        o_excluded=record.get('excluded', ''),
        o_required=record.get('required', '')
    )


def load_from_embed_tb():
    embeddings = block_history_log_embed_tb.objects.all()
    if not embeddings.exists():
        return None

    keyword_embeddings = {}
    for embed in embeddings:
        # VectorField에서 가져온 값을 numpy 배열로 변환
        keyword_embeddings[embed.o_keyword] = np.array(embed.keyword)
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
            'type': record.o_type,
            'category': record.o_category,
            'speaker': record.o_speaker,
            'listener': record.o_listener,
            'Instruction': record.o_instruction,
            'form': record.o_form,
            'excluded': record.o_excluded,
            'required': record.o_required
        }

        # 벡터 레코드 구성 - VectorField에서 가져온 값을 numpy 배열로 변환
        vector_record = {
            'type': np.array(record.v_type),
            'category': np.array(record.v_category),
            'speaker': np.array(record.v_speaker),
            'listener': np.array(record.v_listener),
            'Instruction': np.array(record.v_instruction),
            'form': np.array(record.v_form),
            'excluded': np.array(record.v_excluded),
            'required': np.array(record.v_required)
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
            user_vec = np.array(user_vector[field]) if not isinstance(user_vector[field], np.ndarray) else user_vector[
                field]
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
    excluded_fields = ["type", "category"]

    for field in fields:
        if field not in excluded_fields:  # type과 category를 excluded한 모든 필드에 대해 추천
            freq = defaultdict(int)
            for record in top_records:
                if record.get(field):
                    freq[record[field]] += 1

            # 사용자의 현재 키워드를 excluded하고 정렬
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
    fields = ["type", "category", "speaker", "listener", "instruction", "form", "excluded", "required"]

    try:
        start_time = datetime.now()
        print(f"[process_user_record] 실행 시각: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        # 1. 기존 DB와 벡터 DB 로드
        db_records, db_vector_records = load_from_pca_tb()
        existing_embeddings = load_from_embed_tb() or {}

        # 2. 사용자 입력의 키워드 확인 및 정규화
        def normalize_keyword(kw):
            return kw.strip() if isinstance(kw, str) else kw

        user_keywords = set(normalize_keyword(user_record.get(field)) for field in fields if user_record.get(field) and user_record[field].strip())
        existing_keywords = set(normalize_keyword(kw) for kw in existing_embeddings.keys())

        print(user_keywords)
        print(existing_keywords)

        # 3. 새로운 키워드만 추출
        #new_keywords = user_keywords - existing_keywords
        
        #print(new_keywords)

        #if new_keywords:
            # 4. 새로운 키워드만 임베딩 생성 및 DB 저장
            #feature_extractor = create_embedding_pipeline()
            #new_keyword_embeddings = compute_keyword_embeddings(list(new_keywords), feature_extractor)
            #save_to_embed_tb(new_keyword_embeddings)
            # 기존 임베딩 dict에 추가
            #existing_embeddings.update(new_keyword_embeddings)

            # 5. 모든 키워드 임베딩으로 PCA 진행
            #all_keywords = get_all_keywords(db_records or [], user_record, fields)
            # (혹시 DB에 없는 키워드가 있으면 임베딩 추가)
            #missing_keywords = set(all_keywords) - set(existing_embeddings.keys())
            #if missing_keywords:
                #feature_extractor = create_embedding_pipeline()
                #missing_embeddings = compute_keyword_embeddings(list(missing_keywords), feature_extractor)
                #save_to_embed_tb(missing_embeddings)
                #existing_embeddings.update(missing_embeddings)

            #keyword_embeddings = {kw: existing_embeddings[kw] for kw in all_keywords}
            #embeddings_matrix = np.array([keyword_embeddings[kw] for kw in all_keywords])
            #pca, _ = compute_pca_transform(embeddings_matrix)
            # 6. 사용자 기록 벡터화
            #keyword_to_vector_func = create_keyword_to_vector_func(keyword_embeddings, pca)
            #user_vector_record = record_to_vector(user_record, fields, keyword_to_vector_func)
        #else:
            # 새로운 키워드가 없으면 기존 PCA DB의 벡터만 사용 (PCA fit 제거)
            # user_record의 각 필드 값이 db_records에 존재하면 해당 벡터를, 없으면 [0,0,0] 사용
            #user_vector_record = {}
            #for field in fields:
                #user_value = user_record.get(field)
                #found = False
                #for rec, vec in zip(db_records, db_vector_records):
                    #if rec.get(field) == user_value:
                        #user_vector_record[field] = vec.get(field, [0,0,0])
                        #found = True
                        #break
                #if not found:
                    #user_vector_record[field] = [0,0,0]

        # === 기존 임베딩 DB + 사용자 기록 임베딩을 합쳐 PCA를 fit하는 코드 ===
        # 1. 기존 임베딩 DB에서 모든 임베딩을 불러옴
        all_keywords = get_all_keywords(db_records or [], user_record, fields)
        feature_extractor = create_embedding_pipeline()
        # 2. 사용자 기록의 각 필드 값(키워드)을 임베딩(DB에 없으면 임시로 임베딩)
        keyword_embeddings = existing_embeddings.copy()
        for field in fields:
            user_kw = user_record.get(field)
            if user_kw and user_kw.strip() and user_kw not in keyword_embeddings:
                keyword_embeddings[user_kw] = get_embedding(user_kw, feature_extractor)
        # 3. PCA fit을 위해 기존 임베딩 + 사용자 임베딩 모두 사용
        pca_keywords = list(keyword_embeddings.keys())
        embeddings_matrix = np.array([keyword_embeddings[kw] for kw in pca_keywords])
        pca, transformed_matrix = compute_pca_transform(embeddings_matrix)
        # 4. 각 키워드별 PCA 벡터 매핑
        keyword_pca_vectors = {kw: vec for kw, vec in zip(pca_keywords, transformed_matrix)}
        # 5. 기존 DB 레코드와 사용자 레코드 모두 PCA로 변환
        def get_vector_record(record):
            return {field: keyword_pca_vectors.get(record.get(field), [0,0,0]) for field in fields}
        db_vector_records_pca = [get_vector_record(rec) for rec in db_records]
        user_vector_record = get_vector_record(user_record)

        # 7. 임시로 사용자 기록을 DB에 추가
        if update_db:
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

        # 8. 업데이트된 DB 다시 로드 (새로운 키워드가 있는 경우에만)
        #if new_keywords:
            #db_records, db_vector_records = load_from_pca_tb()

        # 9. 유사도 계산
        #top_indices, similarity_scores = get_top_similar_records(user_vector_record, db_vector_records, fields)
        top_indices, similarity_scores = get_top_similar_records(user_vector_record, db_vector_records_pca, fields)
        top_similar_records = [db_records[idx] for idx in top_indices]

        # 10. 추천 후보 키워드 추출
        recommendations = recommend_keywords(user_record, top_similar_records, fields)

        # 11. 사용자 기록 삭제
        if update_db:
            latest_record = block_history_log_pca_tb.objects.latest('id')
            latest_record.delete()

        # 12. 결과 반환
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        print(f"[process_user_record] 추천 결과: {json.dumps(recommendations, ensure_ascii=False, indent=2)}")
        print(f"[process_user_record] 총 소요 시간: {elapsed:.3f}초")
        return {
            'similar_records': [
                {
                    'record': record,
                    'distance': float(dist)
                }
                for record, (_, dist) in zip(top_similar_records, similarity_scores)
            ],
            'recommendations': recommendations
        }
    except Exception as e:
        print(f"Error in process_user_record: {str(e)}")
        raise 