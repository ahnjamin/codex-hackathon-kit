#!/usr/bin/env python3
"""hook을 일부러 어겨 보고 기대대로 막히는지·통과하는지 본다. 설치 직후와 hook을 고친 뒤에 돌린다.
실행: python3 tools/check-hooks.py   (프로젝트 루트 기준, 하나라도 FAIL이면 종료 코드 1)
이 시험은 hook 스크립트를 직접 부른다. Codex가 실제로 hook을 부르는지는 codex 안에서 /hooks 신뢰 후 확인한다(README).
"""
import datetime, glob, json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
HOOKS = os.path.join(ROOT, ".codex", "hooks")
fails = []


def report(ok, name, detail=""):
    print(f"{'PASS' if ok else 'FAIL'} {name}{('  ' + detail) if detail else ''}")
    if not ok:
        fails.append(name)


def guard(name, path, want, agent=None, shell=None, cwd=ROOT):
    if shell:
        data = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": shell}, "cwd": cwd}
    else:
        patch = path if path.startswith("*** Begin Patch") else f"*** Begin Patch\n*** Update File: {path}\n@@\n-a\n+b\n*** End Patch"
        data = {"hook_event_name": "PreToolUse", "tool_name": "apply_patch", "tool_input": {"command": patch}, "cwd": cwd}
    if agent:
        data["agent_type"] = agent
    got = subprocess.run([sys.executable, os.path.join(HOOKS, "guard.py")], input=json.dumps(data),
                         capture_output=True, text=True).returncode
    report(got == want, name, f"기대={want} 실제={got}")


# 1. guard: apply_patch로 쓰는 길
guard("HUMAN.md 수정은 막는다", "HUMAN.md", 2)
guard("docs/spec.md 수정은 막는다", "docs/spec.md", 2)
guard("NOTES.md 수정은 막는다", "NOTES.md", 2)
guard("tools/ 수정은 막는다", "tools/gate.sh", 2)
guard(".codex/ 수정은 막는다", ".codex/hooks/guard.py", 2)
guard(".gate-base(gate 비교 기준) 수정은 막는다", ".gate-base", 2)
guard("코드 수정은 통과시킨다", "app/main.py", 0)
guard("패치의 Move to로 tools/에 옮기기는 막는다",
      "*** Begin Patch\n*** Update File: app/x.py\n*** Move to: tools/gate.sh\n*** End Patch", 2)

# 1-2. guard: 셸 명령으로 쓰는 길
guard("셸 리다이렉트로 HUMAN.md 덮어쓰기는 막는다", None, 2, shell="echo x > HUMAN.md")
guard("셸 >>로 docs/spec.md 덧붙이기는 막는다", None, 2, shell="echo x >> docs/spec.md")
guard("sed -i로 NOTES.md 고치기는 막는다", None, 2, shell="sed -i '' 's/a/b/' NOTES.md")
guard("sed --in-place=로 NOTES.md 고치기는 막는다", None, 2, shell="sed --in-place=.bak s/a/b/ NOTES.md")
guard("perl -pi로 HUMAN.md 고치기는 막는다", None, 2, shell="perl -pi -e 's/a/b/' HUMAN.md")
guard("sed 스크립트 안의 ;에 속지 않는다", None, 2, shell="sed -i 's/;/,/' NOTES.md")
guard("rm으로 tools/ 지우기는 막는다", None, 2, shell="rm tools/gate.sh")
guard("rm -rf tools(폴더째)는 막는다", None, 2, shell="rm -rf tools")
guard("rm -rf docs(spec.md 포함 폴더)는 막는다", None, 2, shell="rm -rf docs")
guard("rm -rf .(프로젝트 전체)는 막는다", None, 2, shell="rm -rf .")
guard("tee로 .codex/ 쓰기는 막는다", None, 2, shell="echo x | tee .codex/hooks/guard.py")
guard("경로를 돌려 써도(./docs//spec.md) 막는다", None, 2, shell="echo x > ./docs//spec.md")
guard("경로를 돌려 써도(app/../HUMAN.md) 막는다", None, 2, shell="echo x > app/../HUMAN.md")
guard("대소문자를 바꿔도(human.md) 막는다", None, 2, shell="echo x > human.md")
guard("명령을 이어 붙여도(;) 막는다", None, 2, shell="echo a; echo b > HUMAN.md")
guard("mv로 보호 파일을 다른 이름으로 옮기기는 막는다", None, 2, shell="mv HUMAN.md x.md")
guard("cp -t로 tools/에 넣기는 막는다", None, 2, shell="cp -t tools a.sh")
guard("rm -rf *는 막는다", None, 2, shell="rm -rf *")
guard("rm -rf docs/*는 막는다", None, 2, shell="rm -rf docs/*")
guard("rm -rf $PWD(변수)는 막는다", None, 2, shell="rm -rf $PWD")
guard("rm -rf ..(프로젝트를 품은 상위)는 막는다", None, 2, shell="rm -rf ..")
guard("bash -c 안의 쓰기도 막는다", None, 2, shell="bash -c 'echo x > HUMAN.md'")
guard("git rm으로 보호 파일 지우기는 막는다", None, 2, shell="git rm HUMAN.md")
guard("git checkout --로 보호 파일 되돌리기는 막는다", None, 2, shell="git checkout -- NOTES.md")
guard("붙여 쓴 리다이렉트((echo x)>HUMAN.md)도 막는다", None, 2, shell="(echo x)>HUMAN.md")
guard("명령에 '*** Begin Patch' 글자가 있어도 셸 검사를 한다", None, 2, shell="rm -rf tools && echo '*** Begin Patch'")
guard("하위 폴더에서 ../HUMAN.md 쓰기도 막는다", None, 2, shell="echo x > ../HUMAN.md", cwd=os.path.join(ROOT, "app"))
guard("하위 폴더에서 절대경로 쓰기도 막는다", None, 2, shell=f"echo x > {ROOT}/HUMAN.md", cwd=os.path.join(ROOT, "app"))
guard("heredoc 본문의 '> HUMAN.md' 글자는 통과시킨다", None, 0, shell="cat > app/doc.md <<'EOF'\n결과 > HUMAN.md 참고\nEOF")
guard("rm -f *.pyc는 통과시킨다", None, 0, shell="rm -f *.pyc")
guard("app/ 안 mv는 통과시킨다", None, 0, shell="mv app/a.py app/b.py")
guard("보호 파일을 /tmp로 복사(읽기)는 통과시킨다", None, 0, shell="cp HUMAN.md /tmp/backup.md")
guard("cat으로 HUMAN.md 읽기는 통과시킨다", None, 0, shell="cat HUMAN.md")
guard("tools/gate.sh 실행은 통과시킨다", None, 0, shell="sh tools/gate.sh > /dev/null 2>&1")
guard("pytest 실행은 통과시킨다", None, 0, shell="python3 -m pytest -q && echo done")
guard("커밋 메시지 따옴표 안의 -> NOTES.md는 통과시킨다", None, 0, shell='git commit -m "초안 -> NOTES.md 메모"')
guard("코드 폴더 정리(rm -rf app/__pycache__)는 통과시킨다", None, 0, shell="rm -rf app/__pycache__")
guard("cp로 docs/ 폴더에 넣어 spec.md 덮어쓰기는 막는다", None, 2, shell="cp /tmp/spec.md docs/")
guard("cp -r로 tools 폴더째 덮어쓰기는 막는다", None, 2, shell="cp -r /tmp/stuff/tools .")
guard("env bash -c로 감싼 쓰기도 막는다", None, 2, shell="env bash -c 'echo x > HUMAN.md'")
guard("sudo tee도 막는다", None, 2, shell="echo x | sudo tee HUMAN.md")
guard("nohup rm -rf tools도 막는다", None, 2, shell="nohup rm -rf tools")
guard("timeout 5 rm -rf tools도 막는다", None, 2, shell="timeout 5 rm -rf tools")
guard("xargs rm(대상을 알 수 없음)은 막는다", None, 2, shell="xargs rm < list.txt")
guard("rsync로 tools/에 쓰기는 막는다", None, 2, shell="rsync /tmp/x tools/gate.sh")
guard("unlink HUMAN.md는 막는다", None, 2, shell="unlink HUMAN.md")
guard("patch HUMAN.md는 막는다", None, 2, shell="patch HUMAN.md < /tmp/x.diff")
guard("vim으로 NOTES.md 고치기는 막는다", None, 2, shell="vim -c wq NOTES.md")
guard(">&로 HUMAN.md 쓰기는 막는다", None, 2, shell="echo x >&HUMAN.md")
guard("glob으로 HUMAN.md에 쓰기는 막는다", None, 2, shell="echo x > HU*.md")
guard("변수 경로라도 보호 파일 이름이 보이면 막는다", None, 2, shell="echo x > $PWD/HUMAN.md")
guard("find . -exec rm으로 *.md 지우기는 막는다", None, 2, shell="find . -name '*.md' -exec rm {} +")
guard("find tools -delete는 막는다", None, 2, shell="find tools -delete")
guard("rsync -a src/ .(내용물을 프로젝트에 풀기)는 막는다", None, 2, shell="rsync -a /tmp/proj/ .")
guard("rsync -a src/ app/는 통과시킨다", None, 0, shell="rsync -a /tmp/proj/ app/")
guard("find . -name '*.pyc' -delete는 통과시킨다", None, 0, shell="find . -name '*.pyc' -delete")
guard("스킬 보관함에서 꺼내기(cp -r ~/kit/library/...)는 통과시킨다", None, 0, shell="cp -r ~/kit/library/tokens/caveman .agents/skills/")
guard("cp로 app/ 폴더에 넣기는 통과시킨다", None, 0, shell="cp /tmp/a.py app/")
guard("2>&1은 통과시킨다", None, 0, shell="python3 -m pytest -q 2>&1 | tail -3")
guard("env로 감싼 테스트 실행은 통과시킨다", None, 0, shell="env PYTHONPATH=. python3 -m pytest -q")
guard("$TMPDIR 같은 변수 경로 로그 쓰기는 통과시킨다", None, 0, shell="echo x > $TMPDIR/server.log")

# 1-3. guard: 검증 에이전트 제한. 주의: hook 입력의 agent_type 필드에 에이전트 이름이 온다고 가정한 시험이다.
#      Codex가 다른 필드로 보내면 여기는 통과해도 실제로는 안 막힌다(README의 확인 방법으로 실제 확인).
guard("[가정] 검증 에이전트의 코드 수정은 막는다", "app/main.py", 2, agent="verifier")
guard("[가정] 검증 에이전트의 보고서 쓰기는 통과시킨다", "docs/verify/1.md", 0, agent="verifier")
guard("[가정] 검증 에이전트가 셸로 코드 고치기는 막는다", None, 2, agent="verifier", shell="echo x > app/main.py")
guard("[가정] 검증 에이전트가 sed -i로 코드 고치기는 막는다", None, 2, agent="verifier", shell="sed -i '' 's/a/b/' app/main.py")
guard("[가정] 검증 에이전트가 셸로 보고서 쓰기는 통과시킨다", None, 0, agent="verifier", shell="echo ok > docs/verify/1.md")
guard("[가정] 검증 에이전트가 /tmp에 서버 로그 쓰기는 통과시킨다", None, 0, agent="verifier", shell="sh tools/run.sh > /tmp/s.log 2>&1 &")
guard("[가정] 검증 에이전트가 테스트 실행은 통과시킨다", None, 0, agent="verifier", shell="python3 -m pytest -q 2>&1 | tail -3")

# 2. timer: 마감 전후 문구와 형식 오류
sys.path.insert(0, os.path.join(ROOT, "tools"))
import timer, handoff  # noqa: E402

with tempfile.TemporaryDirectory() as d:
    os.makedirs(os.path.join(d, "tools"))
    now = datetime.datetime(2026, 10, 31, 10, 0)

    def timer_lines(env, tasks="| 1 | 가 | 기준 | 진행 | 09:30 |\n| 2 | 나 | 기준 | 대기 | |\n", at=None):
        open(os.path.join(d, "tools", "harness.env"), "w").write(env)
        open(os.path.join(d, "TASKS.md"), "w").write(tasks)
        return "\n".join(timer.lines(d, at or now))

    out = timer_lines('END_AT="13:00"\nSTOP_NEW_MIN="45"\n')
    report("남은 시간 3시간" in out and "대기 중인 큰 작업 1개" in out, "3:00 남으면 남은 시간과 대기 작업 수를 알린다")
    report("1번 '가' 30분째" in out, "진행 작업의 경과 시간을 보여 준다")
    out = timer_lines('END_AT="10:30"\nSTOP_NEW_MIN="45"\n')
    report("새 큰 작업은 시작하지" in out, "45분 아래로 남으면 새 큰 작업 금지를 알린다")
    out = timer_lines('END_AT="09:00"\nSTOP_NEW_MIN="45"\n')
    report("과제 시간이 끝났습니다" in out, "마감이 지나면 끝났다고 알린다")
    out = timer_lines('END_AT="01:00"\nSTOP_NEW_MIN="45"\n', "| 1 | 가 | 기준 | 진행 | 23:50 |\n",
                      at=datetime.datetime(2026, 10, 31, 22, 30))
    report("남은 시간 2시간 30분" in out, "자정을 넘기는 마감(22:30에 01:00)을 다음 날로 읽는다")
    out = timer_lines('END_AT="01:00"\n', "| 1 | 가 | 기준 | 진행 | 23:50 |\n", at=datetime.datetime(2026, 11, 1, 0, 10))
    report("1번 '가' 20분째" in out, "자정 전에 시작한 작업의 경과 시간을 맞게 센다")
    wide = "| 1 | 가 | 기준 | 끝 | 09:00 | app/a.py | 화면 확인 | - |\n| 2 | 나 | 기준 | 진행 | 09:40 | app/b.py | - | 1 |\n| 3 | 다 | 기준 | 대기 | | app/c.py | - | 2 |\n"
    out = timer_lines('END_AT="13:00"\nSTOP_NEW_MIN="45"\n', wide)
    report("2번 '나' 20분째" in out and "대기 중인 큰 작업 1개" in out, "파일·사람 확인·의존 칸이 있어도 타이머가 상태와 시작을 읽는다")
    open(os.path.join(d, "TASKS.md"), "w").write("| # | 작업 | 기준 | 상태 | 시작 | 파일 | 사람 확인 | 의존 |\n|---|---|---|---|---|---|---|---|\n" + wide)
    report(handoff.task_rows(handoff.read(d, "TASKS.md")) == [("1", "가", "끝"), ("2", "나", "진행"), ("3", "다", "대기")],
           "컬럼이 늘어도 handoff가 작업 목록을 읽는다")
    out = timer_lines('END_AT="13:00"\n', "| 1 | 가 | 기준 | 완료 | 09:00 |\n| 2 | [작업] | [기준] | 대기 | |\n")
    report('1번의 상태 "완료"를 읽지 못합니다' in out, "상태 단어가 틀리면(완료) 알린다")
    report("대기 중인 큰 작업" not in out, "템플릿 그대로인 [작업] 줄은 대기 작업으로 세지 않는다")
    out = timer_lines('END_AT="13:00"\nSTOP_NEW_MIN="abc"\n')
    report("STOP_NEW_MIN 형식 오류" in out and "남은 시간 3시간" in out, "STOP_NEW_MIN이 숫자가 아니면 알리고 45분으로 계산한다")
    out = timer_lines('END_AT="25시"\n')
    report("형식 오류" in out, "END_AT 형식이 틀리면 틀렸다고 알린다")
    out = timer_lines('END_AT=""\n')
    report("비어 있습니다" in out, "END_AT이 비면 비었다고 알린다")

# 2-2. 맥락을 넣는 hook의 출력은 JSON이어야 한다. 글자로 내면 Codex가 "invalid ... JSON output"으로 hook을 실패시킨다
def hook_json(script, event):
    r = subprocess.run([sys.executable, os.path.join(ROOT, script)], input=json.dumps({"hook_event_name": event}), capture_output=True, text=True, cwd=ROOT)
    try:
        o = json.loads(r.stdout)["hookSpecificOutput"]
        return o["hookEventName"] == event and "[시간]" in o["additionalContext"]
    except (ValueError, KeyError, TypeError):
        return False


report(hook_json("tools/timer.py", "UserPromptSubmit"), "타이머 hook은 JSON(hookSpecificOutput)으로 낸다")
report(hook_json(".codex/hooks/session_start.py", "SessionStart"), "세션 시작 hook은 JSON(hookSpecificOutput)으로 낸다")

# 3. HANDOFF 빈칸 판정과 Stop hook (임시 git 저장소에서 실제로 돌린다)
with tempfile.TemporaryDirectory() as d:
    os.makedirs(os.path.join(d, "tools"))
    shutil.copy(os.path.join(ROOT, "tools", "handoff.py"), os.path.join(d, "tools"))
    os.makedirs(os.path.join(d, ".codex"))
    g = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", d]

    def write(name, text):
        open(os.path.join(d, name), "w", encoding="utf-8").write(text)

    def stop(active=False):
        p = subprocess.run([sys.executable, os.path.join(HOOKS, "stop.py")], cwd=d, capture_output=True, text=True,
                           input=json.dumps({"hook_event_name": "Stop", "stop_hook_active": active}))
        return p.stdout

    subprocess.run(["git", "init", "-q", d])
    filled = "- 쓴 시각 / 끝낸 작업: 10:00 / 1번 끝\n- 다음 한 걸음: [로그인 화면](app/login.py)의 버튼 고치기\n- 사람이 발견한 것: [버튼] 너무 작음\n"
    write("HANDOFF.md", "- 쓴 시각 / 끝낸 작업: [HH:MM] / [TASKS.md 번호와 한 줄 결과]\n- 다음 한 걸음: [파일·함수·명령까지]\n")
    report(len(handoff.blanks(d)) == 2, "템플릿 그대로인 HANDOFF.md는 빈칸 2줄로 잡는다")
    write("HANDOFF.md", filled)
    report(handoff.blanks(d) == [], "링크([..](..))나 [버튼] 너무 작음 같은 내용은 빈칸으로 보지 않는다")
    write("TASKS.md", "| 1 | 가 | 기준 | 대기 | |\n")
    subprocess.run(g + ["add", "-A"]); subprocess.run(g + ["commit", "-qm", "init"])
    report(stop() == "", "끝난 작업이 없으면 Stop은 막지 않는다")
    auto = os.path.join(d, ".codex", "handoff-auto.md")
    report(os.path.exists(auto) and "1번 가: 대기" in open(auto, encoding="utf-8").read(), "Stop이 자동 기록(.codex/handoff-auto.md)을 쓴다")
    write("NOTES.md", "사람 메모\n")
    subprocess.run(g + ["add", "-A"]); subprocess.run(g + ["commit", "-qm", "notes"])
    write("NOTES.md", "사람 메모\n아직 커밋 안 한 줄\n")
    guard("보호 문서에 커밋 안 된 변경이 있으면 git reset --hard를 막는다", None, 2, shell="git reset --hard", cwd=d)
    guard("보호 문서에 커밋 안 된 변경이 있으면 git checkout -- .을 막는다", None, 2, shell="git checkout -- .", cwd=d)
    guard("그때도 app/만 되돌리기는 통과시킨다", None, 0, shell="git checkout -- app/", cwd=d)
    subprocess.run(g + ["commit", "-qam", "notes2"])
    guard("보호 문서가 깨끗하면 git reset --hard는 통과시킨다", None, 0, shell="git reset --hard", cwd=d)
    write("TASKS.md", "| 1 | 가 | 기준 | 끝 | 09:00 |\n")
    out = stop()
    report('"block"' in out, "작업이 끝났는데 HANDOFF.md를 안 커밋하면 Stop이 막는다")
    report("TASKS.md에 커밋 안 된 변경" in out, "TASKS.md를 안 커밋했으면 그 원인도 알려 준다")
    report(stop(active=True) == "", "이미 한 번 이어 간 턴(stop_hook_active)이면 다시 막지 않는다")
    write("HANDOFF.md", filled.replace("10:00", "10:40"))  # 작업이 끝난 뒤 HANDOFF.md를 새로 쓴다
    subprocess.run(g + ["add", "-A"]); subprocess.run(g + ["commit", "-qm", "handoff"])
    report(stop() == "", "HANDOFF.md를 새로 써서 TASKS.md와 같이 커밋하면 Stop은 막지 않는다")
    write("HANDOFF.md", filled + "- 확인 안 한 것: [추측으로 적은 것]\n")
    subprocess.run(g + ["commit", "-qam", "blank"])
    report("빈칸" in stop(), "커밋했어도 빈칸이 남으면 Stop이 다시 쓰게 한다")

# 4. hooks.json이 가리키는 파일과 에이전트 파일 형식
hooks = json.load(open(os.path.join(ROOT, ".codex", "hooks.json"), encoding="utf-8"))["hooks"]
missing, commands = [], 0
for entries in hooks.values():
    for entry in entries:
        for h in entry["hooks"]:
            commands += 1
            found = re.findall(r"\)/(\S+?\.py)", h["command"])
            if not found:
                missing.append(f"경로를 못 읽음: {h['command']}")
            missing += [rel for rel in found if not os.path.exists(os.path.join(ROOT, rel))]
report(commands > 0 and not missing, "hooks.json의 스크립트가 모두 있다", ", ".join(missing))
try:
    import tomllib  # 3.11부터. macOS 기본 python3(3.9)에는 없다
except ImportError:
    tomllib = None
    print("SKIP 에이전트 toml 형식 검사: 이 python3에는 tomllib이 없다(3.11 이상에서 확인). hook 자체는 3.9에서도 돈다")
if tomllib:
    for role in ("implementer", "verifier"):
        try:
            t = tomllib.load(open(os.path.join(ROOT, ".codex", "agents", f"{role}.toml"), "rb"))
            report(t.get("name") == role and t.get("developer_instructions", "").strip() != "", f"{role}.toml 형식")
        except (OSError, tomllib.TOMLDecodeError) as e:
            report(False, f"{role}.toml 형식", str(e))

# 5. 스킬마다 name·description 머리말이 있어야 Codex가 목록에 올린다
bad = []
for p in sorted(glob.glob(os.path.join(ROOT, ".agents", "skills", "*", "SKILL.md"))):
    head = open(p, encoding="utf-8").read().split("---")
    if len(head) < 3 or not re.search(r"^name:\s*\S", head[1], re.M) or not re.search(r"^description:", head[1], re.M):
        bad.append(os.path.basename(os.path.dirname(p)))
report(not bad, ".agents/skills의 SKILL.md마다 name과 description이 있다", ", ".join(bad))
nested = [os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, ".agents", "skills", "*", "*", "**", "SKILL.md"), recursive=True)]
report(not nested, "스킬 폴더 안에 SKILL.md가 또 없다(있으면 Codex가 스킬을 둘로 읽는다)", ", ".join(nested))

print("\n모두 통과" if not fails else f"\n실패 {len(fails)}건: " + ", ".join(fails))
print("[가정] 항목은 Codex가 hook 입력에 에이전트 이름을 agent_type으로 보낸다는 가정이다. 실제 확인은 README 참고.")
sys.exit(1 if fails else 0)
