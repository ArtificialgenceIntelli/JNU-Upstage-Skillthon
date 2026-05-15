#!/usr/bin/env python3
"""
parse_document.py — Upstage Document Parse로 파일에서 텍스트 추출
Usage: python parse_document.py <file_path>
Output: 마크다운 텍스트를 stdout으로 출력
"""

import sys
import os
from pathlib import Path

# assets/.env에서 API 키 로드
script_dir = Path(__file__).parent
env_path = script_dir.parent / "assets" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

UPSTAGE_API_KEY = os.environ.get("UPSTAGE_API_KEY")
if not UPSTAGE_API_KEY:
    print("Error: UPSTAGE_API_KEY가 설정되지 않았습니다.", file=sys.stderr)
    sys.exit(1)

import requests

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".heic"}


def parse_document(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        print(f"Error: 파일을 찾을 수 없습니다: {file_path}", file=sys.stderr)
        sys.exit(1)

    is_image = path.suffix.lower() in IMAGE_EXTENSIONS

    with open(file_path, "rb") as f:
        form_data = {
            "model": "document-parse",
            "output_formats": '["markdown"]',
        }
        if is_image:
            form_data["ocr"] = "force"

        resp = requests.post(
            "https://api.upstage.ai/v1/document-digitization",
            headers={"Authorization": f"Bearer {UPSTAGE_API_KEY}"},
            files={"document": f},
            data=form_data,
            timeout=120,
        )

    resp.raise_for_status()
    result = resp.json()
    pages_used = result.get("usage", {}).get("pages", "?")
    print(f"[Document Parse 완료: {pages_used}페이지]", file=sys.stderr)

    return result["content"]["markdown"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_document.py <file_path>", file=sys.stderr)
        sys.exit(1)

    text = parse_document(sys.argv[1])
    print(text)
