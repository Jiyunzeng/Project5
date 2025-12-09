# tokenizer.py
from konlpy.tag import Okt
import re

okt = Okt()

def decompose_korean(word):
    """
    복합어를 부분 문자열로 자동 분해
    예: '신한금융' → ['신한금융','신한','금융','신한금','한금']
    """
    result = set()
    word = word.lower()  # 소문자 통일

    n = len(word)
    for i in range(n):
        for j in range(i+2, n+1):  # 최소 2글자 이상
            result.add(word[i:j])

    return list(result)


def tokenize(text):
    if not text:
        return []

    # 1) 소문자로 전부 변환
    text = text.lower()

    # 2) konlpy 기반 명사 추출
    base_tokens = okt.nouns(text)

    final_tokens = set()

    for token in base_tokens:
        token = token.lower()

        # 기본 단어 추가
        final_tokens.add(token)

        # 복합어 분해 추가
        for sub in decompose_korean(token):
            final_tokens.add(sub)

    # 길이가 너무 짧은 단어 제거
    return [t for t in final_tokens if len(t) >= 2]
