#!/usr/bin/env python3
"""Stop: 턴이 끝날 때마다 돈다.
1. 자동 기록(.codex/handoff-auto.md)을 새로 쓴다. 세션이 갑자기 끊겨도 새 세션이 이걸로 이어 간다.
2. 큰 작업이 `끝`이 됐는데 HANDOFF.md를 그 뒤에 커밋하지 않았으면 멈추지 못하게 한다.
   Codex는 block의 reason을 다음 지시로 넣으므로, AI가 이어서 HANDOFF.md를 쓰고 커밋한다.
   HANDOFF.md를 커밋했어도 `[...]` 빈칸이 남았으면 다시 쓰게 한다.
   이미 한 번 이어 간 턴(stop_hook_active)이면 다시 막지 않는다(무한 반복 방지).
Stop hook은 stdout에 JSON만 써야 한다."""
import json, os, subprocess, sys

data = {}
try:
    data = json.load(sys.stdin)
except ValueError:
    pass
root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or os.getcwd()
sys.path.insert(0, os.path.join(root, "tools"))
try:
    import handoff
    with open(os.path.join(root, ".codex", "handoff-auto.md"), "w", encoding="utf-8") as f:
        f.write(handoff.snapshot(root) + "\n")
    reason = ""
    if handoff.tasks_done_since_handoff(root) > 0:
        reason = ("큰 작업이 끝났는데 HANDOFF.md가 그 뒤로 갱신되지 않았습니다. AGENTS.md의 HANDOFF 규칙대로 "
                  "HANDOFF.md를 덮어쓰고 커밋하세요. 그다음 AGENTS.md '사람이 할 일'(직접 써 보기, 코드 읽기, 퀴즈 5문항, NOTES.md)을 "
                  "진행하고, 그게 끝난 뒤에 세션 교체를 권하세요.")
        if subprocess.run(["git", "status", "--porcelain", "--", "TASKS.md"], cwd=root, capture_output=True, text=True).stdout.strip():
            reason += " TASKS.md에 커밋 안 된 변경이 있습니다. HANDOFF.md와 같은 커밋에 TASKS.md도 넣으세요(안 그러면 이 안내가 계속 뜹니다)."
    elif any(r[2] == "끝" for r in handoff.task_rows(handoff.read(root, "TASKS.md"))) and handoff.blanks(root):
        reason = ("HANDOFF.md에 빈칸이 남아 있습니다. 채우거나 쓸 게 없으면 '없음'이라고 쓴 뒤 커밋하세요:\n"
                  + "\n".join(handoff.blanks(root)[:8]))
    if reason and not data.get("stop_hook_active"):
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
except Exception as e:  # hook 오류로 대화가 막히면 안 되지만, 조용히 묻히지 않게 stderr에는 남긴다
    print(f"stop hook 오류: {e}", file=sys.stderr)
