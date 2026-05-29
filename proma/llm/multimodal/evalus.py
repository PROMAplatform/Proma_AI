import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict, Counter
import pandas as pd
from typing import List, Dict, Tuple
from langchain_core.documents import Document
import json


class LangChainRAGEvaluator:
    """LangChain RAG 시스템의 벡터 검색 결과 평가 클래스"""

    def __init__(self, query_fields: Dict[str, str], context_docs: List[Document]):
        """
        Args:
            query_fields: 입력 쿼리 필드들 (예: {"speaker": "교수", "listener": "학생"})
            context_docs: 검색된 Document 객체들의 리스트
        """
        self.query_fields = query_fields
        self.context_docs = context_docs
        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))

    def parse_context_docs(self) -> Dict[str, List[str]]:
        """검색된 문서들을 카테고리별로 파싱"""
        categories = defaultdict(list)

        for doc in self.context_docs:
            content = doc.page_content
            if ':' in content:
                # 'o_' 접두사 제거 후 파싱
                key_value = content.replace('o_', '')
                if ':' in key_value:
                    category, value = key_value.split(':', 1)
                    categories[category.strip()].append(value.strip())

        return dict(categories)

    def calculate_field_match_score(self) -> Dict[str, float]:
        """입력 필드와 검색 결과 간의 매칭 점수 계산"""
        parsed_docs = self.parse_context_docs()
        match_scores = {}

        for field, query_value in self.query_fields.items():
            if field in parsed_docs:
                retrieved_values = parsed_docs[field]

                # 정확 매치 점수
                exact_matches = sum(1 for val in retrieved_values if val.lower() == query_value.lower())
                exact_match_ratio = exact_matches / len(retrieved_values) if retrieved_values else 0

                # 부분 매치 점수 (포함 관계)
                partial_matches = sum(1 for val in retrieved_values
                                      if query_value.lower() in val.lower() or val.lower() in query_value.lower())
                partial_match_ratio = partial_matches / len(retrieved_values) if retrieved_values else 0

                # 의미적 유사성 점수 (TF-IDF 기반)
                all_texts = [query_value] + retrieved_values
                try:
                    tfidf_matrix = self.vectorizer.fit_transform(all_texts)
                    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
                    semantic_score = np.mean(similarities) if len(similarities) > 0 else 0
                except:
                    semantic_score = 0

                # 종합 점수 (가중 평균)
                combined_score = (
                        exact_match_ratio * 0.5 +
                        partial_match_ratio * 0.3 +
                        semantic_score * 0.2
                )

                match_scores[field] = {
                    'exact_match': exact_match_ratio,
                    'partial_match': partial_match_ratio,
                    'semantic_similarity': semantic_score,
                    'combined_score': combined_score,
                    'retrieved_count': len(retrieved_values)
                }
            else:
                # 해당 필드가 검색 결과에 없는 경우
                match_scores[field] = {
                    'exact_match': 0.0,
                    'partial_match': 0.0,
                    'semantic_similarity': 0.0,
                    'combined_score': 0.0,
                    'retrieved_count': 0
                }

        return match_scores

    def calculate_coverage_score(self) -> float:
        """커버리지 점수: 입력 필드 중 얼마나 많은 필드가 검색 결과에 포함되었는지"""
        parsed_docs = self.parse_context_docs()
        covered_fields = len(set(self.query_fields.keys()).intersection(set(parsed_docs.keys())))
        total_fields = len(self.query_fields)

        return covered_fields / total_fields if total_fields > 0 else 0.0

    def calculate_diversity_score(self) -> float:
        """다양성 점수: 각 카테고리별 유니크한 값들의 분포"""
        parsed_docs = self.parse_context_docs()
        diversity_scores = []

        for category, values in parsed_docs.items():
            if len(values) > 0:
                unique_ratio = len(set(values)) / len(values)
                diversity_scores.append(unique_ratio)

        return np.mean(diversity_scores) if diversity_scores else 0.0

    def calculate_relevance_distribution(self) -> Dict[str, float]:
        """관련성 분포: 각 카테고리별 검색 결과 분포의 균등성"""
        parsed_docs = self.parse_context_docs()
        category_counts = {cat: len(values) for cat, values in parsed_docs.items()}
        total_docs = sum(category_counts.values())

        if total_docs == 0:
            return {}

        # 엔트로피 기반 분포 균등성 계산
        probabilities = [count / total_docs for count in category_counts.values()]
        entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
        max_entropy = np.log2(len(category_counts)) if len(category_counts) > 1 else 1

        return {
            'entropy': entropy,
            'normalized_entropy': entropy / max_entropy if max_entropy > 0 else 0,
            'category_distribution': category_counts
        }

    def calculate_silhouette_score(self) -> float:
        """실루엣 점수: 클러스터링 품질 평가"""
        if len(self.context_docs) < 2:
            return 0.0

        # 텍스트 추출 및 벡터화
        texts = [doc.page_content for doc in self.context_docs]

        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)

            # 카테고리별 라벨 생성
            labels = []
            for doc in self.context_docs:
                content = doc.page_content.replace('o_', '')
                if ':' in content:
                    category = content.split(':', 1)[0].strip()
                    labels.append(category)
                else:
                    labels.append('unknown')

            # 라벨을 숫자로 변환
            unique_labels = list(set(labels))
            if len(unique_labels) > 1:
                label_to_num = {label: i for i, label in enumerate(unique_labels)}
                numeric_labels = [label_to_num[label] for label in labels]

                score = silhouette_score(tfidf_matrix.toarray(), numeric_labels)
                return max(0.0, score)  # 음수 점수는 0으로 처리
            else:
                return 0.0
        except Exception as e:
            print(f"실루엣 점수 계산 오류: {e}")
            return 0.0

    def evaluate_comprehensive(self) -> Dict:
        """종합 평가 수행"""
        results = {}

        # 1. 필드별 매칭 점수
        field_matches = self.calculate_field_match_score()
        results['field_match_scores'] = field_matches

        # 2. 전체 매칭 점수 (평균)
        if field_matches:
            avg_combined_score = np.mean([scores['combined_score'] for scores in field_matches.values()])
            results['overall_match_score'] = avg_combined_score
        else:
            results['overall_match_score'] = 0.0

        # 3. 커버리지 점수
        results['coverage_score'] = self.calculate_coverage_score()

        # 4. 다양성 점수
        results['diversity_score'] = self.calculate_diversity_score()

        # 5. 실루엣 점수
        results['silhouette_score'] = self.calculate_silhouette_score()

        # 6. 관련성 분포
        results['relevance_distribution'] = self.calculate_relevance_distribution()

        # 7. 검색 결과 통계
        results['retrieval_stats'] = {
            'total_docs': len(self.context_docs),
            'unique_categories': len(self.parse_context_docs()),
            'query_fields_count': len(self.query_fields)
        }

        # 8. 종합 점수 계산 (각 지표의 가중 평균)
        weights = {
            'overall_match_score': 0.4,  # 가장 중요: 실제 매칭 정도
            'coverage_score': 0.25,  # 커버리지
            'silhouette_score': 0.2,  # 클러스터링 품질
            'diversity_score': 0.15  # 다양성
        }

        final_score = sum(results[key] * weights[key] for key in weights.keys())
        results['final_evaluation_score'] = final_score

        return results

    def print_evaluation_report(self):
        """상세 평가 보고서 출력"""
        results = self.evaluate_comprehensive()

        print("=" * 80)
        print("🔍 LangChain RAG 벡터 검색 평가 보고서")
        print("=" * 80)

        # 종합 점수
        final_score = results['final_evaluation_score']
        print(f"\n📊 최종 평가 점수: {final_score:.3f}")

        if final_score >= 0.8:
            print("   ✅ 매우 우수한 검색 성능")
        elif final_score >= 0.6:
            print("   ✅ 우수한 검색 성능")
        elif final_score >= 0.4:
            print("   ⚠️  적절한 검색 성능")
        elif final_score >= 0.2:
            print("   🔄 개선이 필요한 검색 성능")
        else:
            print("   ❌ 부족한 검색 성능")

        # 세부 점수
        print(f"\n📈 세부 평가 지표:")
        print(f"   - 전체 매칭 점수: {results['overall_match_score']:.3f}")
        print(f"   - 커버리지 점수: {results['coverage_score']:.3f}")
        print(f"   - 클러스터링 품질: {results['silhouette_score']:.3f}")
        print(f"   - 다양성 점수: {results['diversity_score']:.3f}")

        # 필드별 상세 분석
        print(f"\n🎯 필드별 매칭 분석:")
        for field, scores in results['field_match_scores'].items():
            print(f"   📌 {field}:")
            print(f"      - 정확 매치: {scores['exact_match']:.3f}")
            print(f"      - 부분 매치: {scores['partial_match']:.3f}")
            print(f"      - 의미적 유사성: {scores['semantic_similarity']:.3f}")
            print(f"      - 종합 점수: {scores['combined_score']:.3f}")
            print(f"      - 검색된 항목 수: {scores['retrieved_count']}")

        # 검색 통계
        stats = results['retrieval_stats']
        print(f"\n📋 검색 결과 통계:")
        print(f"   - 총 검색된 문서: {stats['total_docs']}개")
        print(f"   - 유니크 카테고리: {stats['unique_categories']}개")
        print(f"   - 입력 필드: {stats['query_fields_count']}개")

        # 카테고리 분포
        dist = results['relevance_distribution']
        if 'category_distribution' in dist:
            print(f"\n📊 카테고리별 분포:")
            for category, count in dist['category_distribution'].items():
                print(f"   - {category}: {count}개")

        print("\n" + "=" * 80)


# 귀하의 기존 함수와 통합하는 래퍼 함수
def evaluate_rag_performance(query_fields: Dict[str, str], context_docs: List[Document]) -> Dict:
    """
    RAG 검색 성능을 평가하는 메인 함수

    Args:
        query_fields: 입력 쿼리 필드들
        context_docs: 벡터 검색으로 찾은 문서들

    Returns:
        평가 결과 딕셔너리
    """

    evaluator = LangChainRAGEvaluator(query_fields, context_docs)
    results = evaluator.evaluate_comprehensive()
    evaluator.print_evaluation_report()

    return results
