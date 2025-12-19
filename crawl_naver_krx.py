# final_crawler_krx_naver.py  ← 이 이름으로 저장해서 매일 돌려
import requests
from bs4 import BeautifulSoup
import pymongo
import redis
from datetime import datetime
import time
import random
from pymongo import UpdateOne
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from zoneinfo import ZoneInfo

# ================== MongoDB + Redis 연결 ==================
mongo_client = pymongo.MongoClient("mongodb+srv://kh:1234@cluster0.fbav0ho.mongodb.net/")
db = mongo_client["stock"]
kospi_col = db["naver_kospi"]
kosdaq_col = db["naver_kosdaq"]

# Redis 연결 (캐시 날리기용)
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_connected = True
    print("Redis 연결 성공")
except:
    r = None
    redis_connected = False
    print("Redis 미연결 → 캐시 갱신 생략")

# 인덱스 자동 생성 (code 기준 unique)
for col, name in [(kospi_col, "naver_kospi"), (kosdaq_col, "naver_kosdaq")]:
    if "code_1" not in col.index_information():
        col.create_index("code", unique=True, name="code_1")
        print(f"[{name}] code 인덱스 생성")
    else:
        print(f"[{name}] code 인덱스 이미 존재")

# ================== Session 설정 ==================
session = requests.Session()
session.headers.update({
    "User-Agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123.0 Safari/537.36"
    ]),
    "Referer": "https://finance.naver.com/",
    "Accept-Language": "ko-KR,ko;q=0.9"
})
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 429])
session.mount("https://", HTTPAdapter(max_retries=retries))

# ================== 숫자 정리 함수 ==================
def clean_int(text):
    if not text or text.strip() in ["N/A", "-", ""]:
        return None
    return int(text.replace(",", ""))

def clean_float(text):
    if not text or text.strip() in ["N/A", "-", ""]:
        return None
    return float(text.replace(",", ""))

# ================== 단일 페이지 크롤링 ==================
def crawl_page(sosok, page):
    url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page={page}"
    try:
        res = session.get(url, timeout=12)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "lxml")
        rows = soup.select("table.type_2 tbody tr[onmouseover]")
        data = []
        today = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 12: continue
            a_tag = cols[1].find("a")
            if not a_tag: continue
            code = a_tag["href"].split("code=")[-1]
            data.append({
                "rank": clean_int(cols[0].get_text(strip=True)),
                "name": a_tag.get_text(strip=True),
                "code": code,
                "current_price": clean_int(cols[2].get_text(strip=True)),
                "change": cols[3].get_text(strip=True),
                "change_rate": cols[4].get_text(strip=True),
                "face_value": clean_int(cols[5].get_text(strip=True)),
                "market_cap": clean_int(cols[6].get_text(strip=True)),
                "listed_shares": clean_int(cols[7].get_text(strip=True)),
                "foreign_ratio": clean_float(cols[8].get_text(strip=True)),
                "volume": clean_int(cols[9].get_text(strip=True)),
                "per": clean_float(cols[10].get_text(strip=True)),
                "roe": clean_float(cols[11].get_text(strip=True)),
                "crawl_date": today,
                "crawled_at": datetime.now(ZoneInfo("Asia/Seoul")),  # 한국 시간 기준
                "market": "KOSPI" if sosok == 0 else "KOSDAQ"
            })
        return data
    except Exception as e:
        print(f"[{'KOSPI' if sosok==0 else 'KOSDAQ'} {page}p] 오류: {e}")
        return []

# ================== 메인 실행 ==================
def run_crawler():
    total_items = 0
    for market_name, sosok, collection in [
        ("KOSPI", 0, kospi_col),
        ("KOSDAQ", 1, kosdaq_col)
    ]:
        print(f"\n{market_name} 크롤링 시작...")
        all_items = []
        empty_streak = 0
        
        for page in range(1, 60):  # 넉넉하게
            items = crawl_page(sosok, page)
            if not items:
                empty_streak += 1
                if empty_streak >= 3:
                    print(f"{market_name} 빈 페이지 연속 → 종료")
                    break
            else:
                empty_streak = 0
                all_items.extend(items)
            print(f"  {page:2d}페이지 → {len(items):3d}개")
            time.sleep(random.uniform(0.3, 0.7))

        # 일괄 업서트
        if all_items:
            ops = [UpdateOne({"code": x["code"]}, {"$set": x}, upsert=True) for x in all_items]
            result = collection.bulk_write(ops, ordered=False)
            print(f"{market_name} 저장 완료 → 삽입 {result.upserted_count}, 수정 {result.modified_count}")
            total_items += len(all_items)
    
    # Redis 캐시 무효화 (중요!)
    if redis_connected and r:
        deleted = r.delete("krx_kospi_list", "krx_kosdaq_list")
        print(f"Redis 캐시 갱신 완료 (삭제된 키: {deleted}개)")

    print(f"\n전체 크롤링 완료! 총 {total_items}개 종목 업데이트")

# ================== 실행 ==================
if __name__ == "__main__":
    start_time = time.time()
    run_crawler()
    print(f"\n소요 시간: {time.time() - start_time:.1f}초")
