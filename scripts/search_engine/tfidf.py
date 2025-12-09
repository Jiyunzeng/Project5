# tfidf.py
from sklearn.feature_extraction.text import TfidfVectorizer

class TfidfRanker:
    def __init__(self, tokenized_docs):
        self.vectorizer = TfidfVectorizer(
            tokenizer=lambda x: x, 
            lowercase=False
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(tokenized_docs)

    def search(self, query_tokens):
        query_vec = self.vectorizer.transform([query_tokens])

        # 모든 문서와 query의 유사도 계산
        scores = (self.tfidf_matrix @ query_vec.T).toarray().ravel()

        ranked_idx = scores.argsort()[::-1]  # 높은 점수 순으로 정렬

        return ranked_idx, scores
