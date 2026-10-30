#!/usr/bin/env python3
"""PreToolUse: 사람이 쓰는 문서와 하네스 파일을 AI가 고치지 못하게 막는다.
파일 수정은 두 길로 온다.
- apply_patch: 패치 안의 `*** Update/Add/Delete File: <경로>`, `*** Move to: <경로>` 줄로 대상을 안다.
- 셸 명령: 리다이렉트(`> 파일`), tee, sed -i, perl -pi, mv(원본 포함), cp, rm(폴더째·glob 포함),
  git rm/mv/checkout/restore, `bash -c '...'` 안의 명령까지 본다. 따옴표 안의 글자와 heredoc 본문은 무시한다.
  git reset --hard, stash, clean, `git checkout -- .`은 보호 문서에 커밋 안 된 변경이 있을 때만 막는다.
경로는 git 루트 기준으로 풀고(하위 폴더에서 열어도 된다) 대소문자를 구분하지 않는다(macOS 대비).
env·sudo·nohup·xargs 같은 감싸는 명령, cp·rsync로 폴더에 넣기, patch·git apply(패치 파일이 이미 있을 때), vim·ed 같은 편집기,
find -delete·-exec rm도 본다.
못 잡는 것: `cd tools && ...`처럼 디렉터리를 옮긴 뒤 쓰기, `python -c` 같은 다른 언어로 쓰기, ln, dd, chmod,
같은 명령 안에서 만든 패치 파일 적용, `$(...)`로 만든 경로. 완전한 차단이 아니라 실수 방지용이다. 보호 문서는 일찍 커밋해 두면 git으로 되살릴 수 있다.
막을 때는 종료 코드 2와 stderr 이유를 쓴다(Codex hook 규칙).
검증 에이전트(verifier)는 docs/verify/ 밑에만 쓸 수 있다. hook 입력에서 에이전트 이름을 찾는 필드는
버전마다 다를 수 있어 몇 개를 본다. 못 찾으면 이 제한은 걸리지 않고(AGENTS.md와 에이전트 지침이 대신한다)
위 보호 목록만 적용된다. 어떤 필드로 오는지 보려면 GUARD_DEBUG=<파일 경로>를 주고 codex를 실행하면
hook 입력이 그 파일에 한 줄씩 남는다."""
import fnmatch, json, os, re, shlex, subprocess, sys

PROTECTED = ("HUMAN.md", "NOTES.md", "docs/spec.md", "tools/", ".codex/")
VERIFIER_OK = "docs/verify/"
ALL_ARGS = {"tee", "rm", "touch", "truncate", "install", "mv", "unlink", "shred",  # 인자 전부가 쓰기 대상
            "vi", "vim", "nvim", "ex", "ed", "nano", "emacs"}
GONE = {"rm", "mv", "unlink", "shred"}  # 원본이 없어진다
WRAPPERS = {"env", "sudo", "doas", "command", "builtin", "exec", "nohup", "time", "nice", "timeout", "stdbuf", "xargs"}
SEPARATORS = {";", "&&", "||", "|", "&", "|&", "(", ")", "{", "}"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>", ">&"}
HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?([^\n]*)\n.*?^\s*\1\s*$", re.S | re.M)


def shell_targets(cmd):
    """셸 명령에서 (쓰기 대상, rm 대상, 넓게 되돌리는 git 명령인지)."""
    cmd = HEREDOC.sub(r"\2", cmd)  # heredoc 본문은 명령이 아니다
    lex = shlex.shlex(cmd.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    try:
        toks = list(lex)
    except ValueError:  # 따옴표가 안 닫힌 경우
        toks = re.findall(r">>?|[^\s>]+", cmd)
    segs, writes, removes, broad, i = [[]], [], [], False, 0
    while i < len(toks):
        t = toks[i]
        if t in REDIRECTS or (t.endswith(">") and set(t) <= set(";&|()>")):  # `)>`, `;>`처럼 붙은 것도
            if i + 1 < len(toks):
                if not (t.endswith("&") and re.fullmatch(r"\d+|-", toks[i + 1])):  # 2>&1 은 파일이 아니다
                    writes.append(toks[i + 1])
                i += 1
            if t[0] in ";&|()":
                segs.append([])
        elif t and (t in SEPARATORS or set(t) <= set(";&|()")):  # sed -i ''의 빈 토큰은 구분자가 아니다
            segs.append([])
        else:
            segs[-1].append(t)
        i += 1
    for seg in segs:
        from_stdin = False
        while seg and (re.fullmatch(r"\w+=\S*", seg[0]) or seg[0].rsplit("/", 1)[-1] in WRAPPERS):
            w, seg = seg[0].rsplit("/", 1)[-1], seg[1:]  # FOO=1 cmd, env/sudo/nohup/xargs cmd 처럼 감싼 것을 벗긴다
            from_stdin = from_stdin or w == "xargs"
            while seg and (seg[0].startswith("-") or (w == "timeout" and re.fullmatch(r"[\d.]+[smhd]?", seg[0]))):
                seg = seg[1:]
        if not seg:
            continue
        name, args = seg[0].rsplit("/", 1)[-1], [t for t in seg[1:] if not t.startswith("-") and t != "<"]
        if from_stdin and (name in ALL_ARGS or name in ("cp", "rsync")):
            removes.append("$(xargs)")  # 대상이 표준입력에서 와서 알 수 없다
        if name in ("bash", "sh", "zsh") and "-c" in seg[1:-1]:
            w, r, b = shell_targets(seg[seg.index("-c") + 1])
            writes, removes, broad = writes + w, removes + r, broad or b
        elif name in ALL_ARGS:
            writes += args
            if name in GONE:
                removes += args + (into_dir(args[-1], args[:-1]) if name == "mv" and len(args) > 1 else [])
        elif name in ("cp", "rsync") and args:
            if any(t.startswith(("-t", "--target")) for t in seg[1:]):
                writes += args
            else:
                extra = into_dir(args[-1], args[:-1])  # cp a docs/ 는 docs/a를 덮어쓴다
                writes += [args[-1]] + extra
                if any(re.match(r"-[A-Za-z]*[rRa]|--recursive|--archive", t) for t in seg[1:]):
                    removes += extra  # 폴더째 복사는 보호 파일을 품은 폴더를 덮어쓸 수 있다
                    if any(x.endswith(("/", "/.")) for x in args[:-1]):
                        removes.append(args[-1])  # rsync -a src/ . 처럼 내용물을 대상 폴더에 바로 푼다
        elif name == "patch":
            src = next((seg[i + 1] for i, t in enumerate(seg[:-1]) if t in ("<", "-i", "--input")), None)
            writes += [a for a in args if a != src] or diff_targets(src)
        elif name == "find" and find_hits(seg):
            writes.append(".")
            removes.append(".")
        elif name in ("sed", "perl") and any(re.match(r"-[A-Za-z]*i|--in-place", t) for t in seg[1:]):
            writes += args[1:]  # 첫 인자는 스크립트
        elif name == "git" and args:
            sub, rest = args[0], args[1:]
            if sub == "apply":
                for a in rest:
                    writes += diff_targets(a)
            elif sub in ("rm", "mv"):
                writes, removes = writes + rest, removes + rest
            elif sub in ("checkout", "restore"):
                paths = seg[seg.index("--") + 1:] if "--" in seg else rest
                writes += paths
                broad = broad or any(contains_protected(norm(p)) for p in paths)
            elif sub == "clean" or sub == "stash" or (sub == "reset" and "--hard" in seg):
                broad = True
    return writes, removes, broad


def into_dir(dest, srcs):
    """dest가 폴더면 그 안에 생길 경로들(cp a b docs/ → docs/a, docs/b)."""
    n = norm(dest)
    if n in ("", "?") or not (dest.endswith("/") or n == "." or os.path.isdir(os.path.join(ROOT, n))):
        return []
    return [os.path.join(dest, os.path.basename(x.rstrip("/"))) for x in srcs if os.path.basename(x.rstrip("/")) not in ("", ".", "..")]


def diff_targets(path):
    """패치 파일이 고치는 경로들. 못 읽으면 빈 목록(같은 명령에서 만든 패치는 못 본다)."""
    try:
        text = open(os.path.join(CWD, path), encoding="utf-8", errors="replace").read() if path else ""
    except OSError:
        return []
    return [m for m in re.findall(r"^(?:\+\+\+|---) (?:[ab]/)?(\S+)", text, re.M) if m != "/dev/null"]


def find_hits(seg):
    """find ... -delete / -exec rm 이 보호 파일까지 지울 수 있는가."""
    if not ("-delete" in seg or any(t in ("-exec", "-execdir", "-ok") and i + 1 < len(seg) and
                                    seg[i + 1].rsplit("/", 1)[-1] in GONE for i, t in enumerate(seg))):
        return False
    roots = []
    for t in seg[1:]:
        if t.startswith("-") or t in ("(", "!"):
            break
        roots.append(t)
    pats = [seg[i + 1].lower() for i, t in enumerate(seg[:-1]) if t in ("-name", "-iname", "-path", "-ipath")]
    for r in roots or ["."]:
        n = norm(r)
        if n == "":
            continue
        if n == "?" or is_protected(n):
            return True
        if contains_protected(n):
            names = {c.lower() for x in PROTECTED for c in x.rstrip("/").split("/")}
            if not pats or any(fnmatch.fnmatch(c, pt.strip("*/") or pt) or fnmatch.fnmatch(c, pt) for pt in pats for c in names):
                return True
    return False


def is_protected(n):
    return any((n + "/").startswith(x.lower()) if x.endswith("/") else n == x.lower() for x in PROTECTED)


def contains_protected(n):
    """n이 보호 파일을 품은 폴더(또는 프로젝트 전체)인가. rm -rf docs, rm -rf . 용."""
    return n == "." or any(x.lower().startswith(n + "/") for x in PROTECTED)


def norm(p):
    """루트 기준 소문자 상대경로. 프로젝트 밖이면 "", 루트나 그 위면 ".", 변수·~가 들어 있어 모르면 "?"."""
    p = p.strip().strip("'\"")
    if not p:
        return ""
    if p.startswith("~") or "$" in p or "`" in p:
        return "?"
    a = os.path.realpath(p if os.path.isabs(p) else os.path.join(CWD, p))
    if a == ROOT or ROOT.startswith(a.rstrip("/") + "/"):
        return "."
    if not a.startswith(ROOT + "/"):
        return ""
    return os.path.relpath(a, ROOT).lower()


def glob_hits(p):
    """rm의 glob 인자(*, ?, [)가 보호 경로에 걸리는가."""
    rel = os.path.normpath(os.path.join(os.path.relpath(CWD, ROOT), p.strip("'\""))).lower()
    return any(fnmatch.fnmatch(x.rstrip("/").lower(), rel) or fnmatch.fnmatch(x.lower().split("/")[0], rel) for x in PROTECTED)


def dirty_protected():
    out = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--", *[x.rstrip("/") for x in PROTECTED]],
                         capture_output=True, text=True).stdout
    return out.strip()


def block(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


try:
    data = json.load(sys.stdin)
except ValueError:
    sys.exit(0)
if os.environ.get("GUARD_DEBUG"):
    with open(os.environ["GUARD_DEBUG"], "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False)[:2000] + "\n")
CWD = os.path.realpath(data.get("cwd") or os.getcwd())
ROOT = os.path.realpath(subprocess.run(["git", "-C", CWD, "rev-parse", "--show-toplevel"],
                                       capture_output=True, text=True).stdout.strip() or CWD)
tool_input = data.get("tool_input") or {}
text = tool_input.get("command") or tool_input.get("patch") or tool_input.get("input") or ""
if isinstance(text, list):
    text = " ".join(map(str, text))
text = str(text)
paths, removes, broad = [tool_input.get("file_path", "")], [], False
if text.lstrip().startswith("*** Begin Patch"):
    paths += re.findall(r"^\*\*\* (?:(?:Update|Add|Delete) File|Move to): (.+?)\s*$", text, re.M)
else:
    w, removes, broad = shell_targets(text)
    paths += w
agent = next((str(data[k]) for k in ("agent_type", "agent_name", "subagent_type", "agent") if data.get(k)), "")

PROTECTED_NAMES = [x.rstrip("/").lower() for x in PROTECTED] + ["human.md", "notes.md", "spec.md"]
for p in paths:
    n = norm(p)
    if n == "?" and any(x in p.lower() for x in PROTECTED_NAMES):
        block(f"{p}에 변수가 있지만 보호 파일 이름이 보입니다. 경로를 그대로 적어 주세요(AGENTS.md).")
    if p and any(c in p for c in "*?[") and n != "?" and glob_hits(p):
        block(f"{p}가 보호 파일(HUMAN.md, NOTES.md, docs/spec.md, tools/, .codex/)에 걸릴 수 있습니다. 파일을 좁혀 주세요.")
    if n in ("", "?"):
        continue
    if is_protected(n) or (p in removes and contains_protected(n)):
        block(f"{p}은(는) 사람이 관리하는 파일이라 AI가 고치지 않습니다(AGENTS.md). 바꿔야 하면 사람에게 물어보세요.")
    if agent == "verifier" and not n.startswith(VERIFIER_OK):
        block(f"검증 에이전트는 코드를 고치지 않습니다({p}). 보고서는 {VERIFIER_OK}<작업번호>.md에만 씁니다.")
for p in removes:
    if norm(p) == "?":
        block(f"지우거나 덮어쓸 대상 {p}에 변수, ~, xargs가 들어 있어 보호 파일을 건드리는지 확인할 수 없습니다. 경로를 그대로 적어 주세요.")
    if any(c in p for c in "*?[") and glob_hits(p):
        block(f"rm {p}가 보호 파일(HUMAN.md, NOTES.md, docs/spec.md, tools/, .codex/)까지 지웁니다. 지울 파일을 좁혀 주세요.")
if broad and dirty_protected():
    block("이 git 명령은 커밋 안 된 사람 문서(HUMAN.md, NOTES.md, docs/spec.md 등)의 변경을 날립니다. "
          "되돌릴 파일만 골라서(예: git checkout -- app/) 하거나 사람에게 먼저 물어보세요.")
