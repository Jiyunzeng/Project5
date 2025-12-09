from pymongo import MongoClient

def load_news():
    try:
        uri = "mongodb+srv://kh:1234@cluster0.fbav0ho.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(uri)
        db = client["stock"]
        col = db["news_crawling"]

        docs = list(col.find({}, {
            "_id": 0,
            "title": 1,
            "description": 1,
            "author": 1,
            "pubDate": 1,
            "pub_date": 1,
            "link": 1,
            "image": 1
        }))

        titles = [d.get("title", "") for d in docs]
        contents = [d.get("description", "") for d in docs]

        return docs, titles, contents

    except Exception as e:
        print("❌ ERROR in load_news():")
        print(e)
        return [], [], []


# 🔥 테스트 코드
if __name__ == "__main__":
    try:
        docs, titles, contents = load_news()
        print("문서 개수:", len(docs))
        print("첫 번째 뉴스 제목:", titles[0] if titles else "없음")
    except Exception as e:
        print("❌ ERROR in main:")
        print(e)
