# StockNews 

![개발 기간](https://img.shields.io/badge/개발%20기간-2025.12.02%20~%202025.12.16-blue?style=flat-square)
![팀원 수](https://img.shields.io/badge/팀원-6명-green?style=flat-square)

> 실시간 주식 시세와 뉴스 데이터를 수집·분석하여 형태소 분석과 TF-IDF 기반 검색을 제공하는 데이터 기반 웹 서비스

<img src="https://github.com/user-attachments/assets/1231967b-c1d3-4f0e-8ad4-81def337bf63" alt="프로젝트 메인 대시보드 스크린샷" />

---

## 📌 프로젝트 개요
StockNews는 **실시간 주식 시세와 뉴스 데이터**를 수집·분석하여,  
**형태소 분석과 TF-IDF 기반 검색 기능**을 제공하는 데이터 기반 웹 서비스 프로젝트입니다.

주식 시세와 뉴스 정보를 함께 확인하기 어려운 환경을 개선하여,  
사용자는 종목 및 키워드를 기준으로 관련 뉴스와 시장 흐름을 한 화면에서 효율적으로 탐색할 수 있습니다.

## 📅 개발 기간
2025.12.02 ~ 2025.12.16

## 👥 팀원 및 역할

| 이름   | 역할                          | GitHub                                                                 |
|--------|-------------------------------|------------------------------------------------------------------------|
| 정태규 | [팀장] 국내주식 크롤링, 실시간 대시보드 등            | [![GitHub](https://img.shields.io/badge/GitHub-000000?style=flat&logo=github&logoColor=white)](https://github.com/KANASIEL) |
| 조슬미 | 국내/해외 뉴스 크롤링, 뉴스페이지 등                  | [![GitHub](https://img.shields.io/badge/GitHub-000000?style=flat&logo=github&logoColor=white)](https://github.com/jseulmi) |
| 서원희 | 국내/해외 뉴스 크롤링, 뉴스페이지 등                  | [![GitHub](https://img.shields.io/badge/GitHub-000000?style=flat&logo=github&logoColor=white)](https://github.com/wonhui29) |
| 구현서 | 로그인/회원가입, 다국어UI 등                         | [![GitHub](https://img.shields.io/badge/GitHub-000000?style=flat&logo=github&logoColor=white)](https://github.com/guhyeonseo) |
| 손원주 | 검색엔진 (형태소 분석 TF-IDF랭킹 오타보정), AI요약 등 | [![GitHub](https://img.shields.io/badge/GitHub-000000?style=flat&logo=github&logoColor=white)](https://github.com/swj6498) |
| **지윤정** | 검색엔진 (형태소 분석 TF-IDF랭킹 오타보정), 인기검색어 등 | [![GitHub](https://img.shields.io/badge/GitHub-000000?style=flat&logo=github&logoColor=white)](https://github.com/Jiyunzeng) |

## ✨ 핵심 기능

- 실시간 국내 주식 시세 조회 (KOSPI / KOSDAQ)
- 국내·해외 주식 뉴스 자동 수집 및 제공
- 형태소 분석 기반 뉴스 검색
- TF-IDF 가중치를 적용한 검색 결과 랭킹 제공
- 검색 로그 기반 인기 검색어 제공
- 자동완성 검색어 제공
- AI 요약 제공
- 다국어 지원

## 👨‍💻 담당 역할

| 역할/영역 | 담당 내용 |
|---|---|
| 🔍 검색 기능 | 뉴스 검색 기능 설계 및 구현 |
| 📊 검색 랭킹 | TF-IDF 가중치 기반 검색 결과 랭킹 로직 구현 |
| 🗂 검색 로그 | 사용자 검색 로그 저장 및 관리 구조 구현 |
| 📈 인기 검색어 | 검색 로그 기반 인기 검색어 기능 구현 |
| ⌨ 자동완성	 | 자동완성 검색어 기능 구현 |

## 🛠️ 기술 스택

| 카테고리             | 기술                                                                                                                                 |
|----------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| 운영체제             | ![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=flat&logo=ubuntu&logoColor=white)&nbsp;![Windows 11](https://img.shields.io/badge/Windows%2011-0078D6?style=flat&logo=windows11&logoColor=white) |
| 언어                 | ![Java](https://img.shields.io/badge/Java-ED8B00?style=flat&logo=openjdk&logoColor=white)&nbsp;![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)&nbsp;![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black) |
| 백엔드 프레임워크    | ![Spring Boot](https://img.shields.io/badge/Spring%20Boot-6DB33F?style=flat&logo=springboot&logoColor=white)&nbsp;![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)&nbsp;![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white) |
| 프론트엔드           | ![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=white)&nbsp;![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white)&nbsp;![Axios](https://img.shields.io/badge/Axios-5A29E4?style=flat&logo=axios&logoColor=white)&nbsp;![Fetch API](https://img.shields.io/badge/Fetch%20API-FF4154?style=flat&logo=javascript&logoColor=white) |
| ORM / 데이터 접근     | ![MyBatis](https://img.shields.io/badge/MyBatis-000000?style=flat&logo=mybatis&logoColor=white)                                       |
| 데이터베이스          | ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)&nbsp;![MongoDB Atlas](https://img.shields.io/badge/MongoDB%20Atlas-47A248?style=flat&logo=mongodb&logoColor=white)&nbsp;![Oracle](https://img.shields.io/badge/Oracle-F80000?style=flat&logo=oracle&logoColor=white) |
| 인증 / 보안          | ![JWT](https://img.shields.io/badge/JWT-000000?style=flat&logo=jsonwebtokens&logoColor=white)&nbsp;![OAuth2](https://img.shields.io/badge/OAuth2-EB5424?style=flat&logo=open%20id&logoColor=white)&nbsp; |
| AI / 외부 API        | ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)&nbsp;![Perplexity.ai](https://img.shields.io/badge/Perplexity.ai-000000?style=flat&logo=perplexity-ai&logoColor=white) ![Naver](https://img.shields.io/badge/Naver-03C75A?style=flat&logo=naver&logoColor=white)&nbsp;![Google](https://img.shields.io/badge/Google-EA4335?style=flat&logo=google&logoColor=white)&nbsp;![Kakao](https://img.shields.io/badge/Kakao-FFCD00?style=flat&logo=kakao&logoColor=black) |
| 배포 / 호스팅        | ![Render](https://img.shields.io/badge/Render-46E3B7?style=flat&logo=render&logoColor=black)                                          |
| 개발 도구 / IDE      | ![IntelliJ IDEA](https://img.shields.io/badge/IntelliJ%20IDEA-000000?style=flat&logo=intellijidea&logoColor=white)&nbsp;![STS](https://img.shields.io/badge/Spring%20Tool%20Suite-6DB33F?style=flat&logo=spring&logoColor=white)&nbsp;![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?style=flat&logo=visualstudiocode&logoColor=white) |
| 형상 관리 / 협업     | ![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)&nbsp;![Notion](https://img.shields.io/badge/Notion-000000?style=flat&logo=notion&logoColor=white) |

## 🔍 핵심 로직 및 구현 상세

### 1. TF-IDF 기반 뉴스 검색 랭킹 구현
기존의 키워드 포함 여부 중심 검색 방식은 연관도가 낮다는 한계가 있었습니다. 이를 해결하기 위해 **TF-IDF 가중치와 코사인 유사도(Cosine Similarity)**를 활용한 랭킹 시스템을 구축했습니다.

* **동작 흐름**: 카테고리별 후보 데이터 선조회 → 제목 및 본문 기반 TF-IDF 벡터화 → 유사도 점수 산출 및 정렬
* **성과**: 단순 키워드 일치가 아닌, 문맥적 연관성이 높은 뉴스를 상위에 노출하여 검색 정확도를 개선했습니다.

<details>
<summary><strong>🔍 핵심 코드 보기</strong></summary>

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# TfidfVectorizer를 활용한 뉴스 벡터화 및 유사도 계산
# max_features: 메모리 효율을 위해 주요 단어 1000개 추출
vectorizer = TfidfVectorizer(max_features=1000, lowercase=False, token_pattern=r"\S+")
tfidf_matrix = vectorizer.fit_transform([query_tokens_str] + doc_tokens)

query_vec = tfidf_matrix[0:1] # 사용자 검색어 벡터
doc_vecs = tfidf_matrix[1:]  # 뉴스 문서들 벡터

# 코사인 유사도를 통한 검색 연관도 점수 산출
scores = cosine_similarity(query_vec, doc_vecs)[0]
</details>

2. 검색 정확도 향상을 위한 점수 보정 로직 (Heuristic Scoring)
통계적 유사도(TF-IDF) 점수만으로는 실제 사용자가 느끼는 '중요도'를 완벽히 반영하기 어렵습니다. 이를 보완하기 위해 뉴스 도메인에 특화된 가중치 시스템을 직접 설계했습니다.

보정 기준:

제목 가중치: 검색어가 뉴스 제목에 포함된 경우 가점 부여.

위치 가중치: 뉴스 본문의 앞부분(상단)에 키워드가 등장할수록 높은 점수 할당.

근접도(Proximity): 여러 키워드가 본문 내에서 서로 가까운 위치에 등장할 경우 가산점 반영.

<details> <summary><strong>⚖️ 점수 보정 가중치 로직 보기</strong></summary>

Python

# 1. 제목 위치 기반 가중치 강화
pos_title = title_lower.find(q_lower)
if pos_title != -1:
    title_pos_score = max(0.05, 0.20 * (1 - pos_title / max(len(title_lower), 1)))
    score += title_pos_score

# 2. 본문 내 키워드 근접도(Proximity) 점수 계산
if len(positions) >= 2:
    positions.sort()
    min_gap = min(positions[i+1] - positions[i] for i in range(len(positions)-1))
    # 키워드 간 거리가 80자 이내일 경우 밀접도가 높다고 판단
    proximity_score = max(0.0, 0.15 * (1 - min_gap / 80))
    score += proximity_score
</details>

3. 데이터 자산화를 위한 검색 로그 저장 구조
검색 요청이 발생할 때마다 사용자의 검색 행태를 분석하기 위해 검색어와 검색 시점을 로그로 기록하는 파이프라인을 구축했습니다.

설계 의도: 누적된 로그를 통해 인기 검색어 집계 및 자동완성 기능의 원천 데이터로 활용.

기술 스택: Spring Boot와 MongoDB를 연동하여 비정형 로그 데이터를 효율적으로 적재.

<details> <summary><strong>💾 검색 로그 저장 로직 (Java) 보기</strong></summary>

Java

// NewsSearchController.java
@GetMapping("/search-tfidf")
public List<Map<String, Object>> searchWithTfidf(@RequestParam("q") String query) {
    // 검색 요청 시마다 로그 객체 생성 및 MongoDB 저장
    SearchLog log = new SearchLog();
    log.setKeyword(query);
    log.setTimestamp(new Date());
    searchLogRepository.save(log); 
    
    return newsService.searchWithTfidfRanking(query, category);
}
</details>

4. MongoDB Aggregation 기반 인기 검색어 기능
저장된 검색 로그를 활용하여 최근 24시간 동안 가장 많이 검색된 키워드를 실시간으로 집계하여 제공합니다.

동작 흐름: 최근 24시간 로그 필터링 → 키워드 그룹화 및 카운트 → 빈도순 정렬 및 상위 5개 추출.

성과: 사용자가 현재 시장의 주요 이슈를 직관적으로 파악하도록 유도.

<details> <summary><strong>🔥 인기 검색어 집계 코드 (Java/MongoDB) 보기</strong></summary>

Java

// NewsServiceImpl.java
public List<Map<String, Object>> getTrendingKeywords(int hours) {
    LocalDateTime since = LocalDateTime.now().minusHours(hours);
    Date sinceDate = Date.from(since.atZone(ZoneId.systemDefault()).toInstant());

    // MongoDB Aggregation 파이프라인 구성
    Aggregation agg = Aggregation.newAggregation(
        Aggregation.match(Criteria.where("timestamp").gte(sinceDate)), // 시간 필터
        Aggregation.group("keyword").count().as("count"),              // 그룹화 및 카운트
        Aggregation.sort(Sort.Direction.DESC, "count"),                // 정렬
        Aggregation.limit(5)                                           // TOP 5 추출
    );

    return mongoTemplate.aggregate(agg, "search_log", Map.class).getMappedResults();
}
</details>

5. 실시간 자동완성 검색어 구현
사용자가 검색어를 입력하는 과정에서 기존 검색 데이터를 기반으로 부분 일치하는 키워드를 실시간으로 제안합니다.

기능 특징: 대소문자 구분 없는(Case-insensitive) 정규식 검색 적용 및 서버 부하 방지.

성과: 검색 입력 편의성을 높이고 원하는 검색어 도달 시간 단축.

<details> <summary><strong>⌨️ 자동완성 검색 로직 (Java/MongoDB) 보기</strong></summary>

Java

// NewsServiceImpl.java
public List<String> getAutocompleteSuggestions(String query) {
    Query searchQuery = new Query();
    // Regex를 활용한 대소문자 무시 부분 일치 검색
    searchQuery.addCriteria(Criteria.where("term").regex(query, "i")); 
    searchQuery.limit(10); 

    List<NewsTerm> results = mongoTemplate.find(searchQuery, NewsTerm.class, "news_terms");
    return results.stream().map(NewsTerm::getTerm).collect(Collectors.toList());
}
</details>

