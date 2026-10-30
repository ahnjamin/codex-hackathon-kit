#!/usr/bin/env python3
"""남은 시간과 지금 작업의 경과 시간을 한 줄씩 출력한다.
UserPromptSubmit hook이 메시지마다 부르고(출력이 AI 맥락에 들어간다), 사람이 직접 돌려도 된다.
- END_AT: 과제가 끝나는 시각. STOP_NEW_MIN 아래로 남으면 새 큰 작업을 시작하지 말라고 알린다.
- 작업별 시간 상한은 없다. TASKS.md에서 `진행`인 작업의 경과 시간과 `대기` 작업 수만 보여 준다.
  남은 시간 안에 못 끝낼 것 같은지는 AI가 보고 사람에게 묻는다(AGENTS.md).
형식이 틀리면 틀렸다고 알린다(조용히 넘어가면 시간 경고가 없는 줄 모른다).
"""
import datetime, os, re, shlex, subprocess


def parse_time(text, now):
    for f in ("%Y-%m-%d %H:%M", "%H:%M"):
        try:
            t = datetime.datetime.strptime(text, f)
        except ValueError:
            continue
        return t if f.startswith("%Y") else now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
    return None


def hm(mins):
    return f"{mins // 60}시간 {mins % 60}분" if mins >= 60 else f"{mins}분"


def read_env(root):
    cfg = {}
    for line in open(os.path.join(root, "tools", "harness.env"), encoding="utf-8"):
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            cfg[k.strip()] = " ".join(shlex.split(v, comments=True))
    return cfg


def task_rows(root):
    """TASKS.md 표에서 번호로 시작하는 줄의 (번호, 작업, 상태, 시작) 목록."""
    path = os.path.join(root, "TASKS.md")
    if not os.path.exists(path):
        return []
    rows = []
    for line in open(path, encoding="utf-8"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and cells[0].isdigit():
            rows.append((cells[0], cells[1], cells[3], cells[4]))
    return rows


def doing_tasks(root):
    """상태가 `진행`인 줄의 (번호, 작업, 시작) 목록."""
    return [(n, t, start) for n, t, s, start in task_rows(root) if s == "진행"]


def pending_count(root):
    """상태가 `대기`인 줄 수. 아직 템플릿 그대로인 `[작업]` 줄은 세지 않는다."""
    return sum(1 for _, t, s, _ in task_rows(root) if s == "대기" and not t.startswith("["))


def bad_status(root):
    """상태가 대기·진행·끝이 아닌 줄. 이런 줄은 Stop hook과 타이머가 못 읽으니 알린다."""
    return [(n, s) for n, _, s, _ in task_rows(root) if s not in ("대기", "진행", "끝")]


def lines(root, now=None):
    now = now or datetime.datetime.now()
    cfg = read_env(root)
    out = []
    end_text = cfg.get("END_AT", "")
    if not end_text:
        out.append("[시간] END_AT이 비어 있습니다. tools/harness.env에 과제가 끝나는 시각을 적어 주세요.")
    else:
        end = parse_time(end_text, now)
        if end is None:
            out.append(f'[시간] END_AT 형식 오류: "{end_text}". 예: "13:00"')
        else:
            if re.fullmatch(r"\d{1,2}:\d{2}", end_text) and (now - end).total_seconds() > 12 * 3600:
                end += datetime.timedelta(days=1)  # 자정을 넘기는 마감(예: 22:30에 END_AT="01:00")
            mins = int((end - now).total_seconds() // 60)
            stop_text = cfg.get("STOP_NEW_MIN", "")
            stop = int(stop_text) if stop_text.isdigit() else 45
            if stop_text and not stop_text.isdigit():
                out.append(f'[시간] STOP_NEW_MIN 형식 오류: "{stop_text}". 45분으로 계산합니다.')
            todo = pending_count(root)
            left = f" 대기 중인 큰 작업 {todo}개." if todo else ""
            if mins <= 0:
                out.append("[시간] 과제 시간이 끝났습니다. 제출만 합니다.")
            elif mins < stop:
                out.append(f"[시간] 남은 시간 {hm(mins)}.{left} 새 큰 작업은 시작하지 말고 고치기·문서·제출만 합니다.")
            else:
                out.append(f"[시간] 남은 시간 {hm(mins)}.{left} 못 끝낼 것 같으면 시연에 안 보이는 기능부터 빼자고 사람에게 묻습니다.")
    for num, status in bad_status(root):
        out.append(f'[작업] TASKS.md {num}번의 상태 "{status}"를 읽지 못합니다. `대기`, `진행`, `끝` 중 하나로만 씁니다'
                   "(아니면 HANDOFF 강제와 경과 시간이 꺼진다).")
    for num, title, start_text in doing_tasks(root):
        start = parse_time(start_text, now) if re.fullmatch(r"\d{1,2}:\d{2}", start_text) else None
        if start is None:
            out.append(f"[시간] {num}번 작업의 시작 시각이 비었거나 형식이 틀렸습니다(HH:MM).")
        else:
            if start > now:
                start -= datetime.timedelta(days=1)  # 자정 전에 시작한 작업
            out.append(f"[시간] {num}번 '{title}' {int((now - start).total_seconds() // 60)}분째.")
    return out


if __name__ == "__main__":
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
        print("\n".join(lines(top or os.getcwd())))  # app/ 같은 하위 폴더에서 열어도 tools/harness.env를 찾는다
    except Exception as e:  # hook이 죽으면 대화가 막히므로 알리기만 한다
        print(f"[시간] 타이머 오류: {e}")
