#!/bin/sh
# 키트를 작업 폴더에 깐다. 사용: sh <키트>/setup.sh [작업 폴더, 기본은 지금 폴더]
# 이미 있는 파일은 덮어쓰지 않는다(과제가 준 README 등을 지키려고).
KIT=$(cd "$(dirname "$0")" && pwd)
DEST=${1:-.}
mkdir -p "$DEST" && cd "$DEST" || exit 1

skipped=$( (cd "$KIT/templates" && find . -type f) | while read -r f; do
  if [ -e "$f" ]; then echo "$f"
  else mkdir -p "$(dirname "$f")" && cp "$KIT/templates/$f" "$f"; fi
done)
[ -n "$skipped" ] && echo "건너뜀(이미 있음) $(echo "$skipped" | wc -l | tr -d ' ')개" && echo "$skipped" | grep -v '^\./\.agents/' | sed 's/^/  /' | head -20
chmod +x tools/*.sh 2>/dev/null

if [ ! -f .codex/hooks.json ] || [ ! -f .agents/skills/quiz/SKILL.md ]; then
  echo "WARN .codex/ 또는 .agents/를 깔지 못했습니다. Codex 샌드박스 안에서 돌리면 이 두 폴더와 .git 쓰기가 막힙니다."
  echo "     hook과 스킬이 빠진 상태입니다. 일반 터미널에서 다시 돌리세요: sh $KIT/setup.sh ."
fi

# 키트의 핵심 파일이 과제 저장소의 같은 이름 파일 때문에 안 깔렸으면 크게 알린다
for f in AGENTS.md .codex/hooks.json .codex/hooks/guard.py .codex/hooks/stop.py tools/gate.sh; do
  cmp -s "$KIT/templates/$f" "$f" || echo "WARN $f가 키트 것과 다릅니다(원래 있던 파일). 키트 규칙·hook이 빠질 수 있으니 $KIT/templates/$f와 합치세요"
done

[ -d .git ] || git init -q
# 이미 .gitignore가 있어서 건너뛴 경우에도 필요한 항목을 빠짐없이. 끝에 줄바꿈이 없으면 먼저 붙인다
[ -s .gitignore ] && [ -n "$(tail -c1 .gitignore)" ] && echo >> .gitignore
for ig in .venv/ .env app.db .codex/handoff-auto.md .gate-base __pycache__/ .pytest_cache/; do
  grep -qxF "$ig" .gitignore 2>/dev/null || { echo "$ig" >> .gitignore; echo "덧붙임: .gitignore에 $ig"; }
done

if [ -z "$(git config user.name)" ] || [ -z "$(git config user.email)" ]; then
  echo "WARN git user.name / user.email이 없어 첫 커밋을 하지 않았습니다. 채점 AI가 git log를 읽으니 설정하고 다시 돌리세요:"
  echo "     git config user.name \"이름\" && git config user.email \"메일\" && sh $KIT/setup.sh ."
elif [ -n "$(git status --porcelain)" ]; then
  git add -A && git commit -qm "chore: 해커톤 키트 깔기 (AGENTS.md, gate, hook, 뼈대)" && echo "첫 커밋 완료" \
    || echo "WARN 첫 커밋 실패: 위 git 설정을 하고 직접 커밋하세요(안 하면 gate의 테스트 느슨해짐 검사가 꺼진다)"
fi

echo
echo "다음 할 일"
echo "1. tools/harness.env의 END_AT에 과제가 끝나는 시각 쓰기 (예: \"13:00\", 자정을 넘기면 \"2026-11-01 01:00\")"
echo "2. python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt"
echo "3. sh tools/gate.sh && python3 tools/check-hooks.py"
echo "4. venv를 켠 셸에서 codex --search --add-dir .git 실행(--add-dir가 없으면 샌드박스가 커밋을 막는다) → /hooks에서 이 폴더 hook 신뢰(안 하면 hook이 경고 없이 꺼져 있다) → 메시지에 [시간] 줄이 붙는지 확인"
echo "5. 다른 세션에서 만든 명세서를 docs/spec.md로 저장 (만드는 법: docs/spec-prompt.md)"
echo "스킬 보관함: $KIT/library (목록은 INDEX.md, 꺼내기: cp -r $KIT/library/<분야>/<스킬> .agents/skills/)"
