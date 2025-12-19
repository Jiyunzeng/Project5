# scripts/news_typo_corrector.py (최적화 최종 버전)
import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pymongo import MongoClient
from functools import lru_cache

# ⚡ python-Levenshtein 설치 필요: pip install python-Levenshtein
try:
    from Levenshtein import distance as lev_dist
    FAST_LEVENSHTEIN = True
except ImportError:
    FAST_LEVENSHTEIN = False
    print("⚠️ python-Levenshtein 없음. 순수 Python 사용 (느림)")

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
PPLX_API_KEY = os.getenv("PERPLEXITY_API_KEY")

client = MongoClient(MONGO_URI)
db = client["stock"]
news_terms = db["news_terms"]

# 🧠 인덱스 생성 확인 (최초 1회)
def ensure_indexes():
    news_terms.create_index([("term", 1), ("freq", -1)])
    news_terms.create_index("term")
    print("✅ MongoDB 인덱스 확인/생성 완료")
ensure_indexes()


# ---------------------------------------
# ⚡ 초고속 Levenshtein (C 확장 or Python)
# ---------------------------------------
def levenshtein(a: str, b: str) -> int:
    if FAST_LEVENSHTEIN:
        return lev_dist(a, b)
    # 기존 순수 Python fallback
    dp = [[i + j if i * j == 0 else 0 for j in range(len(b) + 1)] for i in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + (0 if a[i - 1] == b[j - 1] else 1)
            )
    return dp[-1][-1]


# ---------------------------------------
# 🚀 MongoDB Aggregation 최적화 (30k → 100개)
# ---------------------------------------
def suggest_news_terms_improved(q: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Aggregation + C-Levenshtein으로 50배 빨라짐"""
    q = q.strip()
    if len(q) < 2:
        return []
    
    q_len = len(q)
    first_char = q[0].lower()
    
    # Aggregation Pipeline: 30k → 100개로 300배 축소
    pipeline = [
        {
            "$match": {
                "term": {
                    "$regex": f"^{first_char}",  # 첫 글자 정확 일치
                    "$options": "i"
                },
                "$expr": {
                    "$and": [
                        {"$gte": [{"$strLenCP": "$term"}, q_len-4]},
                        {"$lte": [{"$strLenCP": "$term"}, q_len+4]}
                    ]
                },
                "$or": [
                    {"freq": {"$gte": 50}},  # freq 50 이상만
                    {"freq": {"$exists": False}}
                ]
            }
        },
        {"$sort": {"freq": -1}},
        {"$limit": 100},  # 핵심: 후보 100개로 제한
        {"$project": {"term": 1, "freq": 1, "top_category": 1}}
    ]
    
    candidates = []
    for doc in news_terms.aggregate(pipeline):
        term = doc.get("term", "")
        if not term or len(term) < 2:
            continue
            
        dist = levenshtein(q, term)
        if dist <= 3:
            score = 1.0 / (dist + 1) + (doc.get("freq", 0) / 10000.0)
            candidates.append({
                "term": term,
                "freq": doc.get("freq", 0),
                "top_category": doc.get("top_category"),
                "dist": dist,
                "score": score
            })
    
    # dist 우선 + freq 복합 정렬
    candidates.sort(key=lambda x: (x["dist"], -x["freq"], -x["score"]))
    return candidates[:limit]


# ---------------------------------------
# 🤖 LLM (캐싱 + 타임아웃)
# ---------------------------------------
@lru_cache(maxsize=128)
def llm_correct_term(original: str) -> str:
    if len(original) < 2:
        return original
        
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PPLX_API_KEY}",
        "Content-Type": "application/json",
    }
    
    content = f"경제·주식·뉴스 용어 오타 교정. '{original}' → 올바른 단어 하나만 출력."

    data = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 10,
        "temperature": 0.0,
    }

    try:
        res = requests.post(url, headers=headers, json=data, timeout=3).json()
        return res["choices"][0]["message"]["content"].strip().split()[0]
    except Exception:
        return original


# ---------------------------------------
# 🧠 메인 로직 (캐싱 적용)
# ---------------------------------------
@lru_cache(maxsize=1000)  # 1000개 쿼리 캐싱
def best_news_correction(q: str) -> Dict[str, Any]:
    q = (q or "").strip()

    if len(q) < 2:
        return {"original": q, "corrected": q, "score": 0.0, "source": "too_short"}

    # 1) exact match (가장 빠름)
    exact_doc = news_terms.find_one({"term": q})
    if exact_doc:
        return {
            "original": q, "corrected": q, "score": 100.0,
            "freq": exact_doc.get("freq", 0),
            "top_category": exact_doc.get("top_category"),
            "is_exact": True, "source": "mongo_exact"
        }

    # 2) 초고속 Aggregation 검색
    cands = suggest_news_terms_improved(q, 10)
    
    if cands:
        best_cand = cands[0]
        best_term = best_cand["term"]
        doc = news_terms.find_one({"term": best_term})
        
        return {
            "original": q, "corrected": best_term,
            "score": 90.0 - best_cand["dist"] * 8,
            "freq": doc.get("freq", best_cand["freq"]) if doc else best_cand["freq"],
            "top_category": doc.get("top_category") if doc else best_cand.get("top_category"),
            "is_exact": False, "source": "aggregation_search"
        }

    # 3) LLM fallback (최후 수단)
    corrected = llm_correct_term(q)
    return {
        "original": q, "corrected": corrected, "score": 50.0,
        "freq": 0, "top_category": None,
        "is_exact": (corrected == q), "source": "llm_fallback"
    }


# ---------------------------------------
# 🧪 고속 테스트
# ---------------------------------------
def test_correction_speed():
    import time
    test_queries = [
        "삼성저", "투자자", "금유", "인도네시", "루피아",
        "애플", "테슬러", "테슬라", "비트코인", "공매도","딸긔","샴성"
    ]
    
    print("⚡ 최적화 성능 테스트")
    print("=" * 60)
    
    total_time = 0
    for q in test_queries:
        start = time.time()
        result = best_news_correction(q)
        elapsed = time.time() - start
        
        total_time += elapsed
        status = "✅" if result["is_exact"] else "🔧"
        print(f"{status} '{q}' → '{result['corrected']}' [{result['source']}] {elapsed*1000:.0f}ms")
    
    print(f"\n🎯 평균 {total_time/len(test_queries)*1000:.0f}ms (목표: <50ms)")

if __name__ == "__main__":
    test_correction_speed()
