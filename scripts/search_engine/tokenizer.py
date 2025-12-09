# tokenizer.py
import re

# 간단한 불용어 목록 (원하면 더 추가 가능)
STOPWORDS = {"그리고", "하지만", "관련", "최근", "대한", "기자", "뉴스"}

def decompose_korean(word):
    """단어 내부의 모든 부분 문자열 생성 (최소 2글자 이상)"""
    result = set()
    word = word.lower()

    n = len(word)
    for i in range(n):
        for j in range(i + 2, n + 1):  # 최소 2글자 이상
            result.add(word[i:j])

    return result


def tokenize(text):
    """한국어 + 영어 토큰화 + 복합어 분해까지 지원"""
    if not text:
        return []

    # 1) 소문자로 변환
    text = text.lower()

    # 2) 한글/영문/숫자만 추출 (단어 단위)
    base_tokens = re.findall(r"[가-힣a-zA-Z0-9]+", text)

    final_tokens = set()

    for token in base_tokens:
        token = token.lower()

        # 불용어 제거
        if token in STOPWORDS:
            continue

        # 기본 토큰 저장
        if len(token) >= 2:
            final_tokens.add(token)

        # 복합어 분해 저장
        final_tokens.update(decompose_korean(token))

    # 최종 결과
    return [t for t in final_tokens if len(t) >= 2]
