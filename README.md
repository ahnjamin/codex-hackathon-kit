# codex-hackathon-kit

Codex CLI로 3시간 해커톤을 치르는 하네스. 작업 규칙(AGENTS.md), hook, 검사 스크립트, 스킬을 작업 폴더에 깐다.

## 설치
작업 폴더의 **터미널**에서:
```bash
git clone https://github.com/ahnjamin/codex-hackathon-kit ~/kit && sh ~/kit/setup.sh .
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
sh tools/gate.sh && python3 tools/check-hooks.py
codex --search -s workspace-write --add-dir .git
```
`--search`는 웹 검색, `-s workspace-write --add-dir .git`은 커밋에 필요하다(기본 샌드박스는 `.git` 쓰기를 막고, 폴더를 신뢰하기 전에는 읽기 전용이라 `--add-dir`도 거부된다).

Codex에게 시켜도 받기는 되지만, 기본 샌드박스가 `.codex/`, `.agents/`, `.git` 쓰기를 막아서 hook과 스킬이 빠진다. 그래서 설치는 터미널에서 한다. 키트는 작업 폴더 안에 받지 않는다(제출물에 섞인다).

## Codex를 열고 첫 1분
- `/hooks`에서 이 폴더의 hook 4개를 신뢰한다(폴더 신뢰와 별개다). 안 하면 경고 없이 hook이 꺼져 있다.
- Codex에게 "hook이 넣어 준 `[시간]` 줄이 있으면 옮겨 적어 줘"라고 보낸다. 없다고 하면 hook이 안 도는 것이다.
- `tools/harness.env`의 `END_AT`에 마감 시각을 쓴다.

## 흐름
1. 별도 Terra 세션에서 명세서를 만들어 `docs/spec.md`로 저장한다(`docs/spec-prompt.md`).
2. 레퍼런스 조사 → 큰 작업으로 나누기(`TASKS.md`).
3. 큰 작업마다: 테스트 → 구현 → gate → 검증 → 커밋 → HANDOFF. 다음 구현이 도는 동안 사람은 써 보고, 코드를 읽고, 퀴즈 5문항을 풀고, `NOTES.md`를 쓴다.

필요한 스킬은 `~/kit/library/`에서 꺼낸다(`library/INDEX.md`). 더 자세한 내용은 [DETAILS.md](DETAILS.md).

MIT. library/의 가져온 스킬은 각 폴더의 원본 라이선스를 따른다.
