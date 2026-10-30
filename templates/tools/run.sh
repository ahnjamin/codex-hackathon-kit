#!/bin/sh
# 개발 서버. 미리보기에서 열리려면 0.0.0.0에 띄워야 한다. 미리보기에는 같은 포트를 입력한다.
cd "$(dirname "$0")/.." || exit 1
[ -d .venv/bin ] && PATH="$PWD/.venv/bin:$PATH"
set -a; [ -f .env ] && . ./.env; set +a   # API 키 같은 값은 .env에 둔다(커밋 안 됨)
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --reload
