from flask import Flask, jsonify, request
from flask_cors import CORS
from urllib.parse import unquote
from datetime import datetime
import threading, time, os, asyncio

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import scripts.naver_news_crawler as crawler

app = Flask(__name__)
CORS(app)  # React CORS 허용

# MongoDB Atlas URI를 환경 변수로 설정 (Render에서 설정)
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in Flask")

# Atlas에서 복사한 mongodb+srv://... 그대로 MONGO_URI에 들어가 있어야 함
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client["stock"]
collection = db["news_crawling"]

@app.route("/")
def index():
    return "Flask API is running"

@app.route("/news")
def get_news():
    category = unquote(request.args.get("category", ""))
    page = int(request.args.get("page", 0))
    size = int(request.args.get("size", 5))
    order = request.args.get("order", "desc")  # 'desc' 최신순, 'asc' 오래된순

    query = {"category": category} if category else {}
    news_list = list(collection.find(query, {"_id": 0}))

    for news in news_list:
        try:
            news["pubDate"] = datetime.strptime(
                news.get("pubDate", "1970-01-01 00:00:00"),
                "%Y-%m-%d %H:%M:%S",
            )
        except Exception:
            news["pubDate"] = datetime(1970, 1, 1)

    reverse = (order != "asc")  # asc면 오래된순, 그 외는 최신순
    news_list.sort(key=lambda x: x["pubDate"], reverse=reverse)

    start = page * size
    end = start + size
    content = news_list[start:end]

    for news in content:
        news["pubDate"] = news["pubDate"].strftime("%Y-%m-%d %H:%M:%S")

    return jsonify(
        {
            "content": content,
            "number": page,
            "totalPages": (len(news_list) + size - 1) // size,
        }
    )

@app.route("/news/search")
def search_news():
    q = request.args.get("q", "").strip()
    category = unquote(request.args.get("category", ""))
    page = int(request.args.get("page", 0))
    size = int(request.args.get("size", 5))
    order = request.args.get("order", "desc")  # 'desc' 최신순, 'asc' 오래된순

    if not q:
        return jsonify({"content": [], "number": 0, "totalPages": 0})

    regex = {"$regex": q, "$options": "i"}

    or_query = {
        "$or": [
            {"title": regex},
            {"content": regex},
            {"author": regex},
            {"media": regex},
        ]
    }

    if category:
        query = {"$and": [{"category": category}, or_query]}
    else:
        query = or_query

    news_list = list(collection.find(query, {"_id": 0}))

    for news in news_list:
        try:
            news["pubDate"] = datetime.strptime(
                news.get("pubDate", "1970-01-01 00:00:00"),
                "%Y-%m-%d %H:%M:%S",
            )
        except Exception:
            news["pubDate"] = datetime(1970, 1, 1)

    reverse = (order != "asc")
    news_list.sort(key=lambda x: x["pubDate"], reverse=reverse)

    start = page * size
    end = start + size
    content = news_list[start:end]

    for news in content:
        news["pubDate"] = news["pubDate"].strftime("%Y-%m-%d %H:%M:%S")

    return jsonify(
        {
            "content": content,
            "number": page,
            "totalPages": (len(news_list) + size - 1) // size,
        }
    )

def run_crawler():
    while True:
        asyncio.run(crawler.main())  # 비동기 함수 실행
        time.sleep(3600)  # 1시간마다 실행

if __name__ == "__main__":
    threading.Thread(target=run_crawler, daemon=True).start()
    port = int(os.environ.get("PORT", 8585))
    app.run(host="0.0.0.0", port=port, debug=False)
