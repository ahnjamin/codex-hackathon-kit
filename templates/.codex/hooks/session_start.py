#!/usr/bin/env python3
"""SessionStart: 새 세션이 열리면 HANDOFF.md, 자동 기록, 남은 시간을 맥락에 넣는다.
세션을 넘길 때 사람이 "HANDOFF.md 읽어"라고 말하지 않아도 이어 가게 하려고 만들었다.
HANDOFF.md는 AI가 쓴 판단(정한 것, 조심할 것), 자동 기록은 Stop hook이 남긴 사실(커밋, 작업 상태, 안 올린 변경)이다."""
import json, os, subprocess, sys

root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or os.getcwd()
sys.path.insert(0, os.path.join(root, "tools"))
out = []
try:
    handoff = open(os.path.join(root, "HANDOFF.md"), encoding="utf-8").read()
    if "[HH:MM]" not in handoff:  # 아직 템플릿 그대로면 넣지 않는다
        out.append("[인수인계] 이전 세션이 남긴 HANDOFF.md:\n" + handoff.strip())
except OSError:
    pass
try:
    out.append("[자동 기록] 직전 세션이 끝날 때의 상태:\n" + open(os.path.join(root, ".codex", "handoff-auto.md"), encoding="utf-8").read().strip())
except OSError:
    pass
try:
    import timer
    out += timer.lines(root)
    doing = timer.doing_tasks(root)
    if doing:
        out.append("[작업] 진행 중: " + ", ".join(f"{n}번 {t}" for n, t, _ in doing))
except Exception as e:
    out.append(f"[시간] 타이머 오류: {e}")
out.append("[규칙] AGENTS.md를 따른다. 큰 작업 하나: 테스트 먼저 → 구현(implementer) → gate → 검증(verifier) → 커밋 → TASKS.md `끝` → HANDOFF.md 커밋 → 다음 구현을 백그라운드로 시작하고 사람은 써 보기·코드 읽기·퀴즈 5문항(한 번에)·NOTES.md → 메모·퀴즈 커밋 → 세션 교체 판단.")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(out)}}, ensure_ascii=False))
