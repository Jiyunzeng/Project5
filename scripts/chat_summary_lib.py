import os
import json
import re
from dotenv import load_dotenv
import requests
from typing import Tuple, Optional
from pydantic import BaseModel

# ----------------------
# 환경변수 로드 (.env)
# ----------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")
load_dotenv(env_path)

PPLX_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PPLX_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")

# Pydantic 모델
class ChatSummaryResponse(BaseModel):
    query: str
    summary: str
    is_stock_related: bool
    model_used: str
    explanation_type: str

VALID_MODELS = [
    "sonar-pro", "sonar-large-online", "sonar-small-online", "sonar"
]

# ---------------------------------------------------------------------
# 후처리: 마크다운 제거 + 기호 제거 + 200자 제한
# ---------------------------------------------------------------------
def _postprocess_summary(raw: str, limit: int = 200) -> str:
    """마크다운 제거 + 200자 이내 + 문장 단위로 자연스럽게 자르기"""
    if not raw:
        return ""

    s = raw.strip()

    # 마크다운 및 불필요한 기호 제거
    s = re.sub(r'\[.*?\]\(.*?\)', ' ', s)
    s = re.sub(r'[#*_`>]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()

    if not s:
        return ""

    # 문장 단위로 분리 (. ? ! …)
    sentences = re.split(r'(?<=[.!?])\s+', s)

    output = ""
    for sentence in sentences:
        if not sentence:
            continue

        candidate = (output + " " + sentence).strip()
        if len(candidate) > limit:
            break
        output = candidate

    # 혹시 한 문장도 못 넣은 경우 → 앞부분만 200자만큼 자르기
    if not output:
        output = s[:limit].rstrip()

    # 문장 끝에 마침표가 없으면 붙여줌
    if output and output[-1] not in ".!?":
        output = output + "."

    return output.strip()



# ---------------------------------------------------------------------
# Perplexity API 요청 (새로운 프롬프트)
# ---------------------------------------------------------------------
def ask_perplexity(prompt: str, timeout: int = 20) -> Tuple[Optional[str], Optional[str]]:
    if not PPLX_API_KEY:
        return None, "No API key"

    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {PPLX_API_KEY}"}

    for model in VALID_MODELS:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": """
당신은 검색어 설명 전문가입니다.

규칙은 다음과 같습니다.
1. 출력은 항상 자연스럽고 공손한 한국어 문장으로 작성하며 반드시 '~입니다.' 형태로 끝납니다.
2. 마크다운, 기호(#, *, -, >, `, [], (), 이모지) 등을 절대 사용하지 않습니다.
3. 1~2개 단락으로 구성하며 전체 길이는 200자 이내입니다.
4. 입력이 '단어'라면 그 단어의 기본 의미를 핵심만 간단히 설명합니다.
5. 그 단어가 금융/주식/자산/시장과 관련된 경우 추가로 주식과의 연관성이나 가격 변동 요소를 설명합니다. 반대로 연관이 없다면 주식 관련 내용은 출력하지 않습니다.
6. 입력이 '문장 형태'라면 해당 문장이 뜻하는 개념이나 시세, 주가 등의 일반적 특징을 자연스럽게 설명합니다.
7. 마지막 줄에는 정확히 JSON 한 줄만 출력합니다: {"is_stock": true} 또는 {"is_stock": false}
8. 출력은 반드시 '자연스러운 설명 한 단락 또는 두 단락' + 'JSON 한 줄'의 형식이어야 합니다.
"""
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 250,
            "temperature": 0.1
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if res.status_code == 200:
                content = res.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                if content.strip():
                    return content.strip(), None
        except Exception:
            continue

    return None, "All models failed"


# ---------------------------------------------------------------------
# 통합 요약 생성
# ---------------------------------------------------------------------
def generate_summary(query: str) -> ChatSummaryResponse:
    if PPLX_API_KEY:
        print(f"🤖 AI 분석: {query}...")
        prompt = f"검색어: '{query}'\n위 규칙에 따라 설명문을 생성하세요."

        ai_response, error = ask_perplexity(prompt)

        if ai_response and not error:
            try:
                # JSON 찾기
                lines = [ln.strip() for ln in ai_response.split("\n") if ln.strip()]
                json_line = next((x for x in reversed(lines) if x.startswith("{") and "is_stock" in x), None)

                is_stock = False
                if json_line:
                    stock_info = json.loads(json_line)
                    is_stock = bool(stock_info.get("is_stock", False))

                # JSON 제거
                summary_text = ai_response.replace(json_line, "").strip() if json_line else ai_response

                clean = _postprocess_summary(summary_text, limit=200)

                return ChatSummaryResponse(
                    query=query,
                    summary=clean,
                    is_stock_related=is_stock,
                    model_used="Perplexity AI",
                    explanation_type="ai_stock" if is_stock else "ai_general"
                )

            except Exception:
                clean = _postprocess_summary(ai_response, limit=200)
                lowered = ai_response.lower()
                is_stock = any(x in lowered for x in ["주가", "시세", "주식", "투자", "금값", "비트코인"])
                return ChatSummaryResponse(
                    query=query,
                    summary=clean,
                    is_stock_related=is_stock,
                    model_used="Perplexity AI",
                    explanation_type="ai_general"
                )

    # ---------------------------
    # Mock fallback
    # ---------------------------
    print("📱 Smart Mock 사용...")

    stock_indicators = ["주가", "시세", "삼성", "LG", "SK", "비트코인", "코스피", "금리"]
    is_stock = any(w in query for w in stock_indicators)

    if is_stock:
        summary = f"{query}는 금융 또는 주식과 연관된 개념으로 시장 상황과 가격 변동 요인을 함께 살펴볼 수 있는 대상입니다."
    else:
        summary = f"{query}의 일반적인 의미와 핵심 특징을 간단하게 설명한 내용입니다."

    summary = _postprocess_summary(summary, limit=200)

    return ChatSummaryResponse(
        query=query,
        summary=summary,
        is_stock_related=is_stock,
        model_used="Smart Mock",
        explanation_type="mock"
    )


# ---------------------------------------------------------------------
# FastAPI용 export
# ---------------------------------------------------------------------
def build_summary(query: str) -> ChatSummaryResponse:
    return generate_summary(query)


# ---------------------------------------------------------------------
# 테스트용 실행
# ---------------------------------------------------------------------
if __name__ == "__main__":
    test_queries = ["삼성전자", "딸기 시세", "인공지능", "비트코인 주가", "날씨 변화", "금값"]

    print("🚀 요약 테스트 시작")
    for q in test_queries:
        print("\n==========================================")
        result = generate_summary(q)
        print(f"입력: {q}")
        print(f"설명: {result.summary}")
        print(f"주식관련: {result.is_stock_related}")
        print(f"타입: {result.explanation_type}")
        print(f"모델: {result.model_used}")
