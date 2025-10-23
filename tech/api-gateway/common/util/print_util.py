"""
시간 정보를 포함한 출력 유틸리티
"""
from datetime import datetime
from typing import Any


def tprint(*args, **kwargs):
    """
    현재 시각과 함께 메시지를 출력하는 print 함수

    Args:
        *args: print에 전달할 위치 인자
        **kwargs: print에 전달할 키워드 인자

    Usage:
        tprint("메시지")  # [2024-01-20 15:30:45] 메시지
        tprint("값:", 123)  # [2024-01-20 15:30:45] 값: 123
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}]", *args, **kwargs)


def tprint_separator(char: str = "=", length: int = 80):
    """
    시간과 함께 구분선을 출력

    Args:
        char: 구분선에 사용할 문자 (기본값: "=")
        length: 구분선 길이 (기본값: 80)

    Usage:
        tprint_separator()  # [2024-01-20 15:30:45] ================================================================================
        tprint_separator("-", 40)  # [2024-01-20 15:30:45] ----------------------------------------
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {char * length}")


def tprint_header(message: str, char: str = "=", length: int = 80):
    """
    시간과 함께 헤더 형식으로 출력 (위아래 구분선 포함)

    Args:
        message: 출력할 메시지
        char: 구분선에 사용할 문자 (기본값: "=")
        length: 구분선 길이 (기본값: 80)

    Usage:
        tprint_header("YouTube API 호출")
        # [2024-01-20 15:30:45] ================================================================================
        # [2024-01-20 15:30:45] YouTube API 호출
        # [2024-01-20 15:30:45] ================================================================================
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    separator = char * length
    print(f"[{timestamp}] {separator}")
    print(f"[{timestamp}] {message}")
    print(f"[{timestamp}] {separator}")


def tprint_json(title: str, data: Any, indent: int = 2):
    """
    시간과 함께 JSON 형식 데이터를 출력

    Args:
        title: 출력할 제목
        data: JSON으로 변환할 데이터 (dict, list 등)
        indent: JSON 들여쓰기 수준 (기본값: 2)

    Usage:
        tprint_json("API 응답", {"key": "value"})
    """
    import json
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {title}:")
    # JSON 문자열의 각 줄에 타임스탬프 추가
    json_str = json.dumps(data, indent=indent, ensure_ascii=False)
    for line in json_str.split('\n'):
        print(f"[{timestamp}] {line}")


def tprint_section(title: str, char: str = "─", length: int = 80):
    """
    시간과 함께 섹션 제목 출력 (구분선 포함)

    Args:
        title: 섹션 제목
        char: 구분선에 사용할 문자 (기본값: "─")
        length: 구분선 길이 (기본값: 80)

    Usage:
        tprint_section("채널 정보")
        # [2024-01-20 15:30:45] ────────────────────────────────────────────────────────────────────────────────
        # [2024-01-20 15:30:45] 채널 정보
        # [2024-01-20 15:30:45] ────────────────────────────────────────────────────────────────────────────────
    """
    tprint_header(title, char, length)
