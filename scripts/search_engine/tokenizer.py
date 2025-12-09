import re

def generate_subtokens(word):
    """한글 단어의 부분 문자열 생성 (신한 → 신한금융 매칭 강화를 위해)"""
    result = set()
    n = len(word)
    for i in range(n):
        for j in range(i + 2, n + 1):
            result.add(word[i:j])
    return result


def tokenize(text):
    if not text:
        return []

    # 한글 단어만 추출
    base_tokens = re.findall(r"[가-힣]{2,}", text)

    final_tokens = set()

    for token in base_tokens:
        final_tokens.add(token)

        # "신한" 검색 시 "신한금융"과 연결되도록 확장
        final_tokens.update(generate_subtokens(token))

    return list(final_tokens)
