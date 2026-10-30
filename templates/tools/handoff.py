#!/usr/bin/env python3
"""인수인계에 필요한 사실을 git과 TASKS.md에서 기계적으로 모은다.
- snapshot(): 최근 커밋, 작업 상태, 커밋 안 된 파일. Stop hook이 턴마다 .codex/handoff-auto.md에 써 두고,
  새 세션이 열리면 SessionStart hook이 HANDOFF.md와 함께 읽혀 준다. AI가 잊어도 사실은 남는다.
- tasks_done_since_handoff(): HANDOFF.md를 마지막으로 커밋한 뒤 `끝`이 된 작업 수. Stop hook이 작업별 인수인계를 강제하는 데 쓴다.
- blanks(): HANDOFF.md에 남은 빈칸. Stop hook이 덜 쓴 인수인계를 다시 쓰게 하는 데 쓴다.
직접 돌리면 snapshot을 출력한다.
"""
import datetime, os, re, subprocess


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True).stdout.strip()


def task_rows(text):
    """TASKS.md 표에서 (번호, 작업, 상태) 목록."""
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and cells[3] in ("대기", "진행", "끝"):
            rows.append((cells[0], cells[1], cells[3]))
    return rows


def read(root, name):
    try:
        return open(os.path.join(root, name), encoding="utf-8").read()
    except OSError:
        return ""


def tasks_done_since_handoff(root):
    done_now = sum(1 for r in task_rows(read(root, "TASKS.md")) if r[2] == "끝")
    last = git(root, "log", "-1", "--format=%H", "--", "HANDOFF.md")
    then = git(root, "show", f"{last}:TASKS.md") if last else ""
    done_then = sum(1 for r in task_rows(then) if r[2] == "끝")
    return done_now - done_then


def blanks(root):
    """HANDOFF.md에 남은 빈칸 줄. `- 항목: [안내 문구]`처럼 값이 대괄호 안내문뿐이거나 [HH:MM]이 남은 줄.
    `[로그인 화면](app/login.py)` 같은 링크나 `[버튼] 너무 작음`처럼 내용이 이어지는 줄은 채워진 것으로 본다."""
    placeholder = re.compile(r"^- [^:]+: \[[^\]]+\]( / \[[^\]]+\])*$")
    return [l.strip() for l in read(root, "HANDOFF.md").splitlines()
            if "[HH:MM]" in l or placeholder.match(l.strip())]


def snapshot(root):
    tasks = [f"- {n}번 {t}: {s}" for n, t, s in task_rows(read(root, "TASKS.md"))] or ["- (TASKS.md 비어 있음)"]
    status = subprocess.run(["git", "status", "--short"], cwd=root, capture_output=True, text=True).stdout.rstrip()  # 앞 공백(안 올린 변경 표시)을 지키려고 strip하지 않는다
    out = [f"# 자동 기록 ({datetime.datetime.now():%H:%M})",
           "", "## 작업", *tasks,
           "", "## 최근 커밋", git(root, "log", "-5", "--format=- %h %s") or "- (없음)",
           "", "## 커밋 안 된 변경", status or "(없음)"]
    return "\n".join(out)


if __name__ == "__main__":
    print(snapshot(git(os.getcwd(), "rev-parse", "--show-toplevel") or os.getcwd()))  # app/ 같은 하위 폴더에서 돌려도
