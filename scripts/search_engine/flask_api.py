from flask import Flask, request, jsonify
from tokenizer import tokenize
from tfidf import TfidfRanker
from mongo_loader import load_news

app = Flask(__name__)

print("🟦 [1] MongoDB에서 뉴스 로딩 중...")
docs, titles, contents = load_news()
print(f"🟩 로딩 완료! 문서 수: {len(docs)}")

print("🟦 [2] 전체 문서 형태소 분석 중...")
tokenized_docs = [tokenize(t + " " + c) for t, c in zip(titles, contents)]
print("🟩 형태소 분석 완료!")

print("🟦 [3] TF-IDF 모델 생성 중...")
ranker = TfidfRanker(tokenized_docs)
print("🟩 TF-IDF 모델 생성 성공!")

@app.route("/searchNews")
def search_news():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    print(f"\n🔍 검색 요청 받음: '{query}'")

    query_tokens = tokenize(query)
    ranked_idx, scores = ranker.search(query_tokens)

    result = []
    for idx in ranked_idx[:20]:
        item = docs[idx].copy()
        item["score"] = float(scores[idx])
        result.append(item)

    return jsonify(result)

# 🔥 React가 호출하는 엔드포인트
@app.route("/news/search")
def search_news_alias():
    return search_news()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
