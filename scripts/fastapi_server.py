# fastapi_server.py - 기존 파일에 News Terms Streamer 추가
from typing import List, Dict, Any
import time
import os
import re
import asyncio
import pickle
import hashlib
import json
from collections import Counter, defaultdict
from typing import Set

from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne
from konlpy.tag import Okt
from contextlib import asynccontextmanager

import redis

# ---------- 기존 모듈들 ----------
from nlp_search import enhanced_tokenize
from tfidf_rank_lib import rank_with_tfidf
from ime_converter import to_hangul
from chat_summary_lib import build_summary, ChatSummaryResponse
from news_typo_corrector import best_news_correction

# ---------- 환경변수 ----------
load_dotenv()

# ---------- MongoDB 설정 ----------
MONGO_URI = os.getenv("MONGO_URI")
CATEGORIES = ["금융","증권","산업/재계","중기/벤처","글로벌 경제","생활경제","경제 일반"]

# 전역 변수들 (News Terms용)
mongo_client = None
news_collection = None
news_terms_collection = None
stopwords: Set[str] = None
okt = Okt()
news_terms_task = None

# ---------- FastAPI ----------
app = FastAPI(title="Project5 AI Search API", version="2.4")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Redis ----------
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
CACHE_TTL = 300

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=False
)

# ---------- News Terms 헬퍼 함수들 ----------
def load_stopwords() -> Set[str]:
    """불용어 로드"""
    file_path = "scripts/stopwords_kor.txt"  # scripts 폴더에 맞게 조정
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            stopwords = set()
            for line in f:
                word = line.strip()
                if word and re.match('^[가-힣]+$', word):
                    stopwords.add(word)
        print(f"✅ 불용어 로드 완료: {len(stopwords)}개")
        return stopwords
    except Exception as e:
        print(f"❌ 불용어 로드 실패: {e}")
        return {"있다", "있는", "하다", "되는", "밝혔다", "기자", "등", "통해", "위해"}

def extract_nouns_kor(text: str, stopwords: Set[str]) -> list[str]:
    """Okt + 불용어 제거로 고품질 명사 추출"""
    if not text or len(text.strip()) < 2:
        return []
    
    try:
        nouns = okt.nouns(text)
        filtered_nouns = [
            noun for noun in nouns 
            if (len(noun) >= 2 and 
                re.match('^[가-힣]+$', noun) and 
                noun not in stopwords)
        ]
        return filtered_nouns
    except Exception as e:
        print(f"⚠️ 형태소 분석 실패: {e}")
        words = re.findall(r'[가-힣]{2,}', text)
        return [w for w in words if w not in stopwords]

async def process_single_doc(doc: Dict[str, Any]):
    """단일 문서 처리 후 bulk upsert"""
    title = doc.get("title", "")
    content = doc.get("content", "")
    cat = doc.get("category", "")
    
    if cat not in CATEGORIES:
        return
        
    text = f"{title} {content}".strip()
    nouns = extract_nouns_kor(text, stopwords)
    
    if not nouns:
        return
    
    # Bulk update operations
    bulk_ops = []
    for noun in nouns:
        # 기존 카테고리 freq 확인 후 증가
        existing = await news_terms_collection.find_one({"term": noun})
        current_cat_freq = existing.get("categories", {}).get(cat, 0) if existing else 0
        
        bulk_ops.append(
            UpdateOne(
                {"term": noun},
                {
                    "$inc": {"freq": 1},
                    "$set": {
                        f"categories.{cat}": current_cat_freq + 1
                    },
                    "$setOnInsert": {
                        "top_category": None,
                        "source": "news_crawling"
                    }
                },
                upsert=True
            )
        )
    
    if bulk_ops:
        await news_terms_collection.bulk_write(bulk_ops, ordered=False)
        print(f"✅ [{cat}] {len(nouns)}개 term 업데이트: {nouns[:3]}...")

async def run_news_terms_stream():
    """MongoDB change stream으로 실시간 처리"""
    print("🔍 News Terms Change Stream 시작...")
    
    pipeline = [
        {"$match": {
            "operationType": "insert",
            "fullDocument.category": {"$in": CATEGORIES}
        }}
    ]
    
    while True:
        try:
            async with news_collection.watch(pipeline) as stream:
                async for change in stream:
                    doc = change["fullDocument"]
                    await process_single_doc(doc)
        except Exception as e:
            print(f"❌ Change Stream 오류: {e}")
            await asyncio.sleep(5)

# ---------- FastAPI 생명주기 ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작/종료 시 News Terms 워커 관리"""
    global mongo_client, news_collection, news_terms_collection, stopwords, news_terms_task
    
    # Startup
    print("🚀 MongoDB 연결 중...")
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client["stock"]
    news_collection = db["news_crawling"]
    news_terms_collection = db["news_terms"]
    stopwords = load_stopwords()
    
    # News Terms 워커 시작
    news_terms_task = asyncio.create_task(run_news_terms_stream())
    print("✅ News Terms Streamer 활성화됨")
    
    yield
    
    # Shutdown
    print("🛑 News Terms Streamer 종료 중...")
    if news_terms_task:
        news_terms_task.cancel()
        try:
            await news_terms_task
        except asyncio.CancelledError:
            pass
    if mongo_client:
        mongo_client.close()

app.router.lifespan_context = lifespan

# ---------- 기존 Cache Utils (변경없음) ----------
def get_cache(key: str):
    try:
        data = redis_client.get(key)
        if data:
            return pickle.loads(data)
    except Exception:
        pass
    return None

def set_cache(key: str, value: Any, ttl: int = CACHE_TTL):
    try:
        redis_client.setex(key, ttl, pickle.dumps(value))
    except Exception:
        pass

def make_docs_hash(documents: List[Dict[str, Any]]) -> str:
    ids = [str(d["id"]) for d in documents if "id" in d and d["id"] is not None]
    ids.sort()
    return hashlib.md5(",".join(ids).encode()).hexdigest()

# ---------- 기존 API들 (변경없음) ----------
class NlpRequest(BaseModel):
    query: str

@app.post("/nlp-analyze")
def nlp_analyze(req: NlpRequest):
    tokens = enhanced_tokenize(req.query)
    return {"tokens": tokens, "count": len(tokens)}

class TfidfRequest(BaseModel):
    query: str
    documents: List[Dict[str, Any]]

@app.post("/tfidf-rank")
def tfidf_rank(req: TfidfRequest):
    original_query = req.query.strip()
    correction = best_news_correction(original_query)
    corrected_query = correction["corrected"].strip().lower()
    
    docs_hash = make_docs_hash(req.documents)
    cache_key = f"tfidf:{corrected_query}:{docs_hash}"
    
    cached = get_cache(cache_key)
    if cached:
        cached["cached"] = True
        print("⚡ TF-IDF cache HIT")
        return cached
    
    print("🐢 TF-IDF cache MISS - 계산 중...")
    ranked = rank_with_tfidf(corrected_query, req.documents)
    
    result = {
        "original_query": original_query,
        "corrected_query": corrected_query,
        "correction": correction,
        "ranked_docs": ranked,
        "total": len(ranked),
        "cached": False
    }
    
    set_cache(cache_key, result)
    print(f"✅ TF-IDF 캐시 저장: {cache_key[:30]}...")
    return result

@app.get("/ime-convert")
def ime_convert(q: str):
    return {"original": q, "converted": to_hangul(q or "")}

@app.get("/news-search-correction")
def news_search_correction(q: str):
    original = (q or "").strip()
    ime_q = to_hangul(original)
    base_q = ime_q or original
    cache_key = f"news_corr:{base_q}"

    cached = get_cache(cache_key)
    if cached:
        cached["cached"] = True
        return cached

    news_corr = best_news_correction(base_q)
    result = {
        "original": original,
        "ime_converted": ime_q,
        "news": news_corr,
        "cached": False
    }
    set_cache(cache_key, result)
    return result

class SummaryRequest(BaseModel):
    query: str

@app.post("/chat-summary", response_model=ChatSummaryResponse)
def chat_summary(req: SummaryRequest):
    return build_summary(req.query)

# ---------- 새로운 News Terms API들 ----------
@app.get("/news-terms/health")
async def news_terms_health():
    """News Terms 상태 확인"""
    total_terms = await news_terms_collection.count_documents({})
    return {
        "status": "🟢 running",
        "total_terms": total_terms,
        "categories": CATEGORIES
    }

@app.get("/news-terms/top/{limit}")
async def get_top_terms(limit: int = 50):
    """상위 용어 조회"""
    pipeline = [
        {"$addFields": {"total_freq": {"$sum": "$categories"}}},
        {"$sort": {"total_freq": -1}},
        {"$limit": limit},
        {"$project": {
            "term": 1,
            "freq": 1,
            "categories": 1,
            "top_category": 1
        }}
    ]
    cursor = news_terms_collection.aggregate(pipeline)
    terms = await cursor.to_list(length=limit)
    return {"terms": terms, "total": len(terms)}

@app.post("/news-terms/rebuild")
async def rebuild_terms(background_tasks: BackgroundTasks):
    """전체 재구축 (백그라운드)"""
    background_tasks.add_task(build_full_terms)
    return {"status": "rebuild started"}

async def build_full_terms():
    """초기 전체 데이터 재구축"""
    print("🔄 News Terms 전체 재구축 시작...")
    await news_terms_collection.delete_many({})
    
    total_counter = Counter()
    category_counters = defaultdict(Counter)
    
    async for doc in news_collection.find({"category": {"$in": CATEGORIES}}):
        text = f"{doc.get('title', '')} {doc.get('content', '')}".strip()
        nouns = extract_nouns_kor(text, stopwords)
        if nouns:
            total_counter.update(nouns)
            category_counters[doc.get("category", "")].update(nouns)
    
    docs = []
    for term, freq in total_counter.most_common(30000):
        cat_freqs = {cat: int(category_counters[cat][term]) for cat in CATEGORIES if category_counters[cat][term] > 0}
        top_category = max(cat_freqs, key=cat_freqs.get, default=None) if cat_freqs else None
        docs.append({
            "term": term,
            "freq": int(freq),
            "categories": cat_freqs,
            "top_category": top_category,
            "source": "news_crawling",
        })
    
    if docs:
        await news_terms_collection.insert_many(docs)
        print(f"✅ 전체 재구축 완료: {len(docs)}개")

# ---------- 기존 Health (확장) ----------
@app.get("/health")
def health_check():
    return {
        "status": "🟢 healthy",
        "redis": "connected" if redis_client.ping() else "disconnected",
        "news_terms": "enabled",
        "version": "2.4"
    }

# ---------- Run ----------
if __name__ == "__main__":
    print("🚀 Project5 AI Search API v2.4 (News Terms Streamer 포함)")
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
