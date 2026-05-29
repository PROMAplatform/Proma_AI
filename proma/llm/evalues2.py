import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from typing import List, Dict
from sklearn.metrics.pairwise import euclidean_distances
from langchain_core.documents import Document

class SimpleRAGEvaluator:
    """클러스터링 품질, 다양성, 의미적 유사도만 평가"""

    def __init__(self, query_fields: Dict[str, str], context_docs: List[Document]):
        self.query_fields = query_fields
        self.context_docs = context_docs
        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))

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
            tfidf_matrix = self.vectorizer.fit_transform(texts)
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
                score = silhouette_score(tfidf_matrix.toarray(), numeric_labels)
                return max(0.0, score)
            else:
                return 0.0
        except Exception as e:
            print(f"실루엣 점수 계산 오류: {e}")
            return 0.0

    def calculate_semantic_similarity(self) -> Dict[str, float]:
        """필드별 의미적 유사도 계산 (중복 제거)"""
        parsed_docs = self.parse_context_docs()
        print(parsed_docs)
        print("dkdkdkdkdkdkdkdkdkdkd")
        semantic_scores = {}
        for field, query_value in self.query_fields.items():
            if field in parsed_docs:
                # 중복 제거
                retrieved_values = list(set(parsed_docs[field]))
                all_texts = [query_value] + retrieved_values
                try:
                    tfidf_matrix = self.vectorizer.fit_transform(all_texts)
                    print(tfidf_matrix)
                    print("asdfasdf")
                    # distances = euclidean_distances(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
                    #
                    # # (선택) 유사도 점수로 변환: 0~1 사이 값
                    # similarities = 1 / (1 + distances)
                    # semantic_score = np.mean(similarities) if len(similarities) > 0 else 0
                    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
                    print(similarities)
                    print("111111111")
                    semantic_score = np.mean(similarities) if len(similarities) > 0 else 0
                except:
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
def evaluate_rag_simple(query_fields: Dict[str, str], context_docs: List[Document]) -> Dict:
    evaluator = SimpleRAGEvaluator(query_fields, context_docs)
    results = evaluator.evaluate()
    print("클러스터링 품질(실루엣):", results["silhouette_score"])
    print("다양성 점수:", results["diversity_score"])
    print("의미적 유사도:", results["semantic_similarity"])
    return results
