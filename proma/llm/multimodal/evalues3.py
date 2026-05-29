# 사전 설치 필요: pip install sentence-transformers

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from typing import List, Dict
from langchain_core.documents import Document

from sklearn.metrics.pairwise import euclidean_distances
class SimpleRAGEvaluatorBERT:
    """클러스터링 품질, 다양성, 의미적 유사도(BERT 임베딩)만 평가"""

    def __init__(self, query_fields: Dict[str, str], context_docs: List[Document]):
        self.query_fields = query_fields
        self.context_docs = context_docs
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 경량 BERT 임베딩 모델

    def parse_context_docs(self) -> Dict[str, List[str]]:
        categories = defaultdict(list)
        for doc in self.context_docs:
            content = doc.page_content
            if ':' in content:
                key_value = content.replace('o_', '')
                if ':' in key_value:
                    category, value = key_value.split(':', 1)
                    categories[category.strip()].append(value.strip())
        return dict(categories)

    def calculate_diversity_score(self) -> float:
        parsed_docs = self.parse_context_docs()
        diversity_scores = []
        for category, values in parsed_docs.items():
            if len(values) > 0:
                unique_ratio = len(set(values)) / len(values)
                diversity_scores.append(unique_ratio)
        return np.mean(diversity_scores) if diversity_scores else 0.0

    def calculate_silhouette_score(self) -> float:
        if len(self.context_docs) < 2:
            return 0.0
        texts = [doc.page_content for doc in self.context_docs]
        try:
            # BERT 임베딩 사용
            embeddings = self.model.encode(texts)
            labels = []
            for doc in self.context_docs:
                content = doc.page_content.replace('o_', '')
                if ':' in content:
                    category = content.split(':', 1)[0].strip()
                    labels.append(category)
                else:
                    labels.append('unknown')
            unique_labels = list(set(labels))
            if len(unique_labels) > 1:
                label_to_num = {label: i for i, label in enumerate(unique_labels)}
                numeric_labels = [label_to_num[label] for label in labels]
                score = silhouette_score(embeddings, numeric_labels)
                return max(0.0, score)
            else:
                return 0.0
        except Exception as e:
            print(f"실루엣 점수 계산 오류: {e}")
            return 0.0

    def calculate_semantic_similarity(self) -> Dict[str, float]:
        parsed_docs = self.parse_context_docs()
        semantic_scores = {}
        for field, query_value in self.query_fields.items():
            if field in parsed_docs:
                # 중복 제거
                retrieved_values = list(set(parsed_docs[field]))
                all_texts = [query_value] + retrieved_values
                try:
                    # BERT 임베딩 계산
                    embeddings = self.model.encode(all_texts)
                    # 쿼리 임베딩과 나머지 임베딩 간 코사인 유사도 계산
                    similarities = cosine_similarity([embeddings[0]], embeddings[1:]).flatten()
                    semantic_score = np.mean(similarities) if len(similarities) > 0 else 0

                except Exception as e:
                    print(f"의미적 유사도 계산 오류: {e}")
                    semantic_score = 0
                semantic_scores[field] = semantic_score
            else:
                semantic_scores[field] = 0.0
        return semantic_scores

    def evaluate(self) -> Dict:
        return {
            "silhouette_score": self.calculate_silhouette_score(),
            "diversity_score": self.calculate_diversity_score(),
            "semantic_similarity": self.calculate_semantic_similarity()
        }

# 사용 예시
def evaluate_rag_simple_bert(query_fields: Dict[str, str], context_docs: List[Document]) -> Dict:
    evaluator = SimpleRAGEvaluatorBERT(query_fields, context_docs)
    results = evaluator.evaluate()
    print("클러스터링 품질(실루엣):", results["silhouette_score"])
    print("다양성 점수:", results["diversity_score"])
    print("의미적 유사도:", results["semantic_similarity"])
    return results
