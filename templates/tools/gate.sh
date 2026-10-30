#!/bin/sh
# 큰 작업을 마칠 때 한 번 돌리는 검사. 단계마다 한 줄 요약과 FAIL·WARN 줄만 보여 준다(토큰 아끼기).
# 설정이 비었거나 틀렸으면 통과로 치지 않는다(아무것도 안 돌았는데 PASS가 나오면 안 된다).
cd "$(dirname "$0")/.." || exit 1
. tools/harness.env
[ -d .venv/bin ] && PATH="$PWD/.venv/bin:$PATH"   # venv를 안 켠 셸에서 불러도 설치한 pytest를 쓴다
fail=0

if [ -z "$TEST_ALL" ]; then echo "FAIL TEST_ALL이 비어 있음(tools/harness.env)"; fail=1
else
  out=$(sh -c "$TEST_ALL" 2>&1)
  if [ $? -eq 0 ]; then echo "PASS 전체 테스트 ($(echo "$out" | tail -1))"; else echo "FAIL 전체 테스트"; echo "$out" | tail -30; fail=1; fi
fi

# 기존 테스트가 느슨해졌는지(막지는 않고 알린다): 지워진 검사 줄, 새로 붙은 skip, 테스트 설정 변경.
# 비교 기준은 지난번 gate가 통과한 커밋(.gate-base)이다. Codex 샌드박스가 .codex/ 쓰기를 막아 루트에 둔다. 그 사이에 커밋해 버린 변경도 잡으려고.
base=$(cat .gate-base 2>/dev/null)
git rev-parse --verify -q "$base^{commit}" >/dev/null 2>&1 || base=HEAD
if ! git rev-parse --verify -q HEAD >/dev/null 2>&1; then
  echo "WARN 첫 커밋이 없어 테스트가 느슨해졌는지 검사하지 못함(git user.name·user.email을 설정하고 커밋하세요)"
elif [ -z "$TEST_DIR" ] || [ ! -d "$TEST_DIR" ]; then
  echo "FAIL 테스트 폴더가 없음: \"$TEST_DIR\" (tools/harness.env의 TEST_DIR 확인)"; fail=1
else
  diff=$(git diff "$base" -U0 -- "$TEST_DIR")
  removed=$(echo "$diff" | grep -E '^-' | grep -vE '^---' | grep -E "$ASSERT_PATTERN")
  skipped=$(echo "$diff" | grep -E '^\+' | grep -vE '^\+\+\+' | grep -E "$SKIP_PATTERN")
  config=""
  for c in $TEST_CONFIG; do
    [ -n "$(git diff --name-only "$base" -- "$c" 2>/dev/null)$(git status --porcelain -- "$c" 2>/dev/null)" ] && config="$config $c"
  done
  if [ -n "$removed$skipped$config" ]; then
    echo "WARN 기존 테스트가 느슨해졌을 수 있음(기준 $(git rev-parse --short "$base")) → 사람 확인 전에는 커밋하지 않는다(AGENTS.md)"
    [ -n "$removed" ] && echo "  지워지거나 바뀐 검사 줄:" && echo "$removed" | head -8
    [ -n "$skipped" ] && echo "  새로 붙은 skip:" && echo "$skipped" | head -8
    [ -n "$config" ] && echo "  바뀐 테스트 설정:$config"
  else echo "PASS 기존 테스트 기준 그대로(기준 $(git rev-parse --short "$base"))"; fi
fi

missing=""
[ -z "$SRC_DIRS" ] && missing=" (SRC_DIRS가 비어 있음)"
for d in $SRC_DIRS; do [ -d "$d" ] || missing="$missing $d"; done
if [ -n "$missing" ]; then echo "FAIL 코드 폴더가 없음:$missing (tools/harness.env의 SRC_DIRS 확인)"; fail=1
else
  set -f  # CODE_GLOBS의 *가 현재 폴더 파일로 펼쳐지지 않게
  long=$(for g in $CODE_GLOBS; do find $SRC_DIRS $TEST_DIR -type f -name "$g"; done | while read -r f; do
    n=$(awk 'END { print NR }' "$f"); [ "$n" -gt "$MAX_LINES" ] && echo "  $f: ${n}줄"; done)  # 마지막 줄에 줄바꿈이 없어도 센다
  set +f
  if [ -z "$long" ]; then echo "PASS 코드 파일($CODE_GLOBS) ${MAX_LINES}줄 이하"; else echo "FAIL ${MAX_LINES}줄 넘는 파일"; echo "$long"; fail=1; fi
fi

if [ $fail -eq 0 ]; then
  git rev-parse -q --verify HEAD > .gate-base 2>/dev/null  # 다음 gate의 비교 기준
  echo "gate 통과"
else echo "gate 실패"; fi
exit $fail
