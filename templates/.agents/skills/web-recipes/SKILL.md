---
name: web-recipes
description: 이 키트의 기본 스택(FastAPI + 정적 HTML/JS + SQLite)으로 웹 서비스를 빨리 세우는 조각 모음. 화면 추가, JSON API, 저장, 폼, 외부 API 키, 미리보기 접속, 테스트를 처음 붙일 때 쓴다. 스택이 다르면(React, Next.js) library/frontend의 스킬을 꺼내 쓴다.
---

# web-recipes

새 의존성을 넣기 전에 여기 있는 것으로 되는지 먼저 본다. `requirements.txt`에는 fastapi, uvicorn, httpx, pytest만 있다.

## 서버와 미리보기
- `sh tools/run.sh`가 `0.0.0.0:8000`에 띄운다. localhost에만 띄우면 웹 IDE 미리보기에서 안 열린다.
- 미리보기는 포트와 경로를 입력해서 연다. 시연할 경로를 README에 적는다.

## 정적 화면 + JSON API
```python
# app/main.py
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def index():
    return open("app/static/index.html", encoding="utf-8").read()
```
```html
<!-- app/static/index.html -->
<script type="module">
  const res = await fetch("/api/items");
  if (!res.ok) { document.body.textContent = "불러오지 못했습니다"; throw new Error(res.status); }
  const items = await res.json();
</script>
```
- 같은 서버에서 화면과 API를 같이 주면 CORS 설정이 필요 없다.
- 화면 파일도 300줄 검사 대상으로 하려면 사람에게 `CODE_GLOBS`에 `*.js *.html`을 넣어 달라고 한다.

## 저장: SQLite(표준 라이브러리)
```python
import sqlite3
DB = "app.db"  # .gitignore에 넣는다

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

with db() as con:
    con.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, title TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
```
- 값은 꼭 `?` 자리표시자로 넣는다(`con.execute("... WHERE id = ?", (item_id,))`). 문자열로 붙이지 않는다.
- 테스트에서는 `DB`를 임시 파일로 바꾼다(`monkeypatch.setattr(main, "DB", tmp_path / "t.db")`).

## 입력 검증
```python
from pydantic import BaseModel, Field
class ItemIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)

@app.post("/api/items", status_code=201)
def create(item: ItemIn): ...
```
- 잘못된 입력은 FastAPI가 422로 돌려준다. 화면에서 422를 사람이 읽을 문장으로 바꿔 보여 준다.

## 외부 API 키
- 키는 `.env`에 두고(`.gitignore`에 이미 있다) `os.environ.get("KEY")`로 읽는다. 코드·문서·커밋에 쓰지 않는다.
- 키가 없을 때 앱이 죽지 않고 "키가 없습니다"를 보여 주게 한다. 시연 직전에 키가 없어도 화면은 떠야 한다.
- 서비스 안에서 AI API를 써도 되는지는 대회 규칙을 사람에게 먼저 확인한다.

## 테스트
- API: `fastapi.testclient.TestClient`로 `tests/`에 쓴다(`tests/test_main.py` 참고). 빠르고 브라우저가 필요 없다.
- 화면 e2e: `webapp-testing` 스킬(Playwright). `pip install playwright && python -m playwright install chromium`이 웹 IDE에서 안 되면 API 테스트와 사람이 직접 써 보기로 대신하고 `docs/verify/<번호>.md`에 그렇게 적는다.

## 다크 패턴 피하기(검증에서 본다)
- 취소·삭제 버튼을 숨기거나 흐리게 하지 않는다. 확인 창 문구에 죄책감을 주지 않는다.
- 기본값으로 동의 체크를 켜 두지 않는다. 가격·제한은 누르기 전에 보인다.
