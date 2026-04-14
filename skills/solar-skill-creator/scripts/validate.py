"""
solar-skill-creator: Skill validator
Checks that a skill directory meets Skillthon submission requirements.

Usage:
    python skills/solar-skill-creator/scripts/validate.py <skill-name>
    python skills/solar-skill-creator/scripts/validate.py summarize-receipt

Requirements:
    pip install pyyaml
"""
import re
import sys
from pathlib import Path
from typing import List, Tuple

try:
    import yaml
except ImportError:
    print("오류: pyyaml이 설치되지 않았습니다.")
    print("  pip install pyyaml  실행 후 다시 시도하세요.")
    sys.exit(1)


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from a markdown file."""
    if not content.startswith("---"):
        return {}
    end = content.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(content[4:end]) or {}
    except yaml.YAMLError:
        return {}


def validate(skill_dir: Path) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    # 1. SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md 파일이 없습니다")
        return errors, warnings

    content = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)

    name = str(fm.get("name", "") or "").strip()
    description = str(fm.get("description", "") or "").strip()

    if not name:
        errors.append("SKILL.md: 'name' 필드가 없습니다")
    else:
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            errors.append(
                f"SKILL.md: 'name'이 kebab-case가 아닙니다 → '{name}'\n"
                "  소문자, 하이픈만 사용 가능합니다 (예: summarize-receipt)"
            )
        if len(name) > 64:
            errors.append(f"SKILL.md: 'name'이 64자를 초과합니다 ({len(name)}자)")
        if name != skill_dir.name:
            errors.append(
                f"SKILL.md: 'name'({name})이 디렉토리 이름({skill_dir.name})과 다릅니다\n"
                "  둘 중 하나를 맞춰주세요."
            )
    if not description or "TODO" in description:
        errors.append(
            "SKILL.md: 'description'이 비어있거나 TODO가 남아있습니다\n"
            "  WHAT(무엇을 하는가) + WHEN(언제 쓰는가)을 1024자 이내로 작성하세요."
        )
    elif len(description) > 1024:
        errors.append(f"SKILL.md: 'description'이 1024자를 초과합니다 ({len(description)}자)")

    # 2. skill/main.py
    main_py = skill_dir / "skill" / "main.py"
    if not main_py.exists():
        errors.append("skill/main.py 파일이 없습니다")
    else:
        main_content = main_py.read_text(encoding="utf-8")
        if "def run(" not in main_content:
            errors.append("skill/main.py: run() 함수가 없습니다")
        if "UPSTAGE_API_KEY" not in main_content:
            errors.append(
                "skill/main.py: UPSTAGE_API_KEY를 사용하지 않습니다\n"
                "  os.environ.get('UPSTAGE_API_KEY')로 API 키를 읽어야 합니다."
            )
        if "upstage.ai" not in main_content:
            errors.append(
                "skill/main.py: Upstage API base_url이 없습니다\n"
                "  base_url='https://api.upstage.ai/v1' 을 추가하세요."
            )
        if "TODO" in main_content:
            warnings.append("skill/main.py: TODO 항목이 남아있습니다")
        if 'if __name__ == "__main__"' not in main_content:
            warnings.append("skill/main.py: __main__ 블록이 없습니다 (실행 예시 권장)")

    # 3. requirements.txt
    req = skill_dir / "requirements.txt"
    if not req.exists():
        errors.append("requirements.txt 파일이 없습니다")
    else:
        req_text = req.read_text(encoding="utf-8")
        if "openai" not in req_text:
            errors.append(
                "requirements.txt: 'openai' 패키지가 없습니다\n"
                "  openai>=1.0.0 을 추가하세요."
            )

    # 4. README.md — 6개 섹션 (평가 항목 매핑)
    readme = skill_dir / "README.md"
    if not readme.exists():
        errors.append("README.md 파일이 없습니다")
    else:
        readme_content = readme.read_text(encoding="utf-8")
        required_sections = [
            ("라이프스타일 문제", "주제 적합성 섹션 (15점)"),
            ("스킬 개요", "창의성 섹션 (30점)"),
            ("기술 스택", "구현 완성도 섹션 (25점)"),
            ("Iteration", "개선 과정 섹션 (구현 완성도 25점)"),
            ("사용 방법", "사용자 편의성 섹션 (20점)"),
            ("확장 계획", "사용 가능성 섹션 (10점)"),
        ]
        for keyword, label in required_sections:
            if keyword not in readme_content:
                errors.append(f"README.md: {label} → '{keyword}' 섹션이 없습니다")
        if readme_content.count("TODO") > 3:
            warnings.append(
                f"README.md: TODO 항목이 {readme_content.count('TODO')}개 남아있습니다\n"
                "  제출 전 모든 TODO를 실제 내용으로 채우세요."
            )

    # 5. 보안
    gitignore = (skill_dir.parent / ".gitignore")
    if not gitignore.exists():
        warnings.append(
            ".gitignore 파일이 없습니다 (API 키 노출 위험)\n"
            "  repo 루트에 .gitignore를 추가하고 .env를 포함하세요."
        )
    elif ".env" not in gitignore.read_text():
        warnings.append(".gitignore: '.env'가 포함되지 않았습니다 (API 키 노출 위험)")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("사용법: python skills/solar-skill-creator/scripts/validate.py <skill-name>")
        print("예시:   python skills/solar-skill-creator/scripts/validate.py summarize-receipt")
        sys.exit(1)

    # Resolve skill directory relative to repo root
    repo_root = Path(__file__).resolve().parents[3]
    skill_dir = repo_root / sys.argv[1]

    if not skill_dir.exists():
        print(f"오류: '{skill_dir}' 디렉토리를 찾을 수 없습니다.")
        sys.exit(1)

    print(f"검증 중: {skill_dir.name}\n")
    errors, warnings = validate(skill_dir)

    if warnings:
        print("⚠️  경고 (제출은 가능하나 개선 권장):")
        for w in warnings:
            for line in w.splitlines():
                print(f"   {line}")
        print()

    if errors:
        print("❌ 오류 (수정 후 제출하세요):")
        for e in errors:
            for line in e.splitlines():
                print(f"   {line}")
        print(f"\n총 {len(errors)}개 오류.")
        sys.exit(1)
    else:
        print("✅ 검증 통과! Skillthon 제출 요건을 충족합니다.")
        if warnings:
            print(f"   (경고 {len(warnings)}개는 선택 개선사항입니다)")


if __name__ == "__main__":
    main()
