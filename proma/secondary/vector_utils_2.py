import numpy as np
from transformers import pipeline
from sklearn.decomposition import PCA
from .models import block_history_log_embed_tb, block_history_log_pca_tb
import json
from datetime import datetime

def get_all_keywords_flat(db_records, user_record, fields):
    # 모든 필드의 값을 한데 모아 중복 없이 리스트로 반환
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

def save_to_embed_tb(keyword_embeddings):
    for keyword, embedding in keyword_embeddings.items():
        existing_embed = block_history_log_embed_tb.objects.filter(o_keyword=keyword).first()
        if existing_embed:
            existing_embed.keyword = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            existing_embed.save()
        else:
            block_history_log_embed_tb.objects.create(
                o_keyword=keyword,
                keyword=embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            )

def load_from_embed_tb():
    embeddings = block_history_log_embed_tb.objects.all()
    if not embeddings.exists():
        return None
    keyword_embeddings = {}
    for embed in embeddings:
        keyword_embeddings[embed.o_keyword] = np.array(embed.keyword)
    return keyword_embeddings

def load_from_pca_tb():
    records = block_history_log_pca_tb.objects.all()
    if not records.exists():
        return []
    db_records = []
    for record in records:
        original_record = {
            'type': record.o_type,
            'category': record.o_category,
            'speaker': record.o_speaker,
            'listener': record.o_listener,
            'instruction': record.o_instruction,
            'form': record.o_form,
            'excluded': record.o_excluded,
            'required': record.o_required
        }
        db_records.append(original_record)
    return db_records

def process_user_record_anyway2(user_record, update_db=True):
    # 필드 구분 없이 모든 값을 모아서 추천
    fields = ["type", "category", "speaker", "listener", "instruction", "form", "excluded", "required"]
    try:
        start_time = datetime.now()
        print(f"[process_user_record_anyway] 실행 시각: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        db_records = load_from_pca_tb()
        existing_embeddings = load_from_embed_tb() or {}

        # 모든 필드의 값을 한데 모아 전체 키워드 후보 생성
        all_keywords = get_all_keywords_flat(db_records or [], user_record, fields)
        feature_extractor = create_embedding_pipeline()
        keyword_embeddings = existing_embeddings.copy()
        for kw in all_keywords:
            if kw and kw.strip() and kw not in keyword_embeddings:
                keyword_embeddings[kw] = get_embedding(kw, feature_extractor)
        embeddings_matrix = np.array([keyword_embeddings[kw] for kw in all_keywords])
        pca, transformed_matrix = compute_pca_transform(embeddings_matrix)
        keyword_pca_vectors = {kw: vec for kw, vec in zip(all_keywords, transformed_matrix)}

        # 사용자 입력의 모든 값(키워드) 임베딩
        user_keywords = set(user_record.get(field) for field in fields if user_record.get(field) and user_record[field].strip())
        user_vectors = [keyword_pca_vectors[kw] for kw in user_keywords if kw in keyword_pca_vectors]

        # 전체 후보(모든 필드의 값)에서 사용자 입력과의 평균 거리로 추천
        candidate_scores = []
        for kw in all_keywords:
            if kw in user_keywords:
                continue  # 이미 사용자가 가진 값은 제외
            vec = keyword_pca_vectors[kw]
            # 사용자 입력 벡터들과의 평균 거리
            if user_vectors:
                dists = [np.linalg.norm(vec - user_vec) for user_vec in user_vectors]
                score = np.mean(dists)
            else:
                score = 0
            candidate_scores.append((kw, score))

        # 거리 기준으로 정렬(가까운 것, 먼 것 모두 실험 가능)
        candidate_scores.sort(key=lambda x: x[1])
        # 상위 5개 추천
        recommendations = [kw for kw, score in candidate_scores[:5]]

        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        print(f"[process_user_record_anyway] 추천 결과: {json.dumps(recommendations, ensure_ascii=False, indent=2)}")
        print(f"[process_user_record_anyway] 총 소요 시간: {elapsed:.3f}초")
        return {
            'recommendations': recommendations
        }
    except Exception as e:
        print(f"Error in process_user_record_anyway: {str(e)}")
        raise
