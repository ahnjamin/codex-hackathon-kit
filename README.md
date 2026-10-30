# codex-hackathon-kit

3시간짜리 해커톤에서 Codex CLI와 함께 쓰는 작업 규칙, 검사 스크립트, hook, 빈 뼈대 모음이다.
명세서 → 레퍼런스 조사 → 큰 작업 반복(구현 → 검사 → 별도 검증 → 인수인계 → 사람이 써 보고 퀴즈) 흐름을 hook과 스크립트로 지키게 한다.

## 들어 있는 것
| 파일 | 하는 일 |
|---|---|
| `LICENSE` | MIT. library/의 가져온 스킬은 각 폴더의 원본 라이선스를 따른다 |
| `AGENTS.md` | Codex가 읽는 규칙. 흐름(spec → 레퍼런스 조사 → 큰 작업 분해 → 큰 작업 반복), 사람이 할 일, 퀴즈, 문서 규칙 |
| `HUMAN.md` | 사람이 쓰는 목표·성공 기준·범위. AI는 고치지 않는다 |
| `docs/spec.md` | 다른 세션에서 만들어 가져오는 명세서(처음엔 없음). AI는 고치지 않는다 |
| `docs/spec-prompt.md` | 명세서를 만드는 프롬프트. 대회 Codex에서 Terra로 연 별도 세션에 붙여 쓴다 |
| `TASKS.md` | 큰 작업 목록. 개수는 spec을 보고 정한다. 상태와 시작 시각 |
| `docs/refs.md` | spec의 MVP 기능별로 가져다 쓸 만한 공개 코드·라이브러리. 큰 작업으로 나누기 전에 조사한다 |
| `docs/verify.md` | 검증 체크리스트(gate, e2e, 다크 패턴). 결과는 `docs/verify/<번호>.md` |
| `HANDOFF.md` | 큰 작업이 끝날 때마다 쓰는 인수인계(판단만) |
| `QUIZ.md` | 큰 작업마다 내는 객관식 5문항 중 틀린 것과 해설 |
| `NOTES.md` | 사람이 직접 쓰는 "왜 이렇게 만들었나" 메모. 서술형 대비용 |
| `DECISIONS.md` | 무엇을 왜 골랐는지 한 줄씩 |
| `README.md` | 제출용 틀. 실행 방법, 확인한 것, 남은 한계 |
| `tools/gate.sh` | 큰 작업을 마칠 때 돌리는 검사: 전체 테스트, 테스트가 느슨해졌는지, 300줄 넘는 파일 |
| `tools/check-hooks.py` | hook을 일부러 어겨 보고 기대대로 막히는지 본다. 설치 직후에 돌린다 |
| `tools/timer.py` | 남은 시간과 지금 작업의 경과 시간. 작업별 상한은 없다 |
| `tools/run.sh` | 개발 서버를 `0.0.0.0`에 띄운다 |
| `tools/handoff.py` | 인수인계에 쓸 사실(최근 커밋, 작업 상태, 안 올린 변경)을 모은다 |
| `.codex/agents/` | `implementer`(구현)와 `verifier`(검증, 코드 수정 불가) |
| `.codex/hooks.json` | 아래 hook 넷을 건다 |
| `.agents/skills/` | Codex가 자동으로 읽는 기본 스킬 8개(brainstorm, quiz, web-recipes, webapp-testing 등) |
| `app/`, `tests/` | FastAPI + pytest 빈 뼈대 |

키트 폴더의 `library/`는 작업 폴더로 복사되지 않는 스킬 보관함이다. 과제를 보고 필요한 것만 `cp -r ~/kit/library/<분야>/<스킬> .agents/skills/`로 꺼낸다. 목록, 출처, 라이선스는 [library/INDEX.md](library/INDEX.md).

hook이 하는 일:
- 세션 시작: HANDOFF.md와 자동 기록, 남은 시간을 읽혀 준다.
- 메시지마다: 남은 시간, 대기 중인 큰 작업 수, 지금 작업의 경과 시간을 알린다.
- 턴이 끝날 때(Stop): 자동 기록을 새로 쓰고, 작업이 `끝`이 됐는데 HANDOFF.md를 안 썼으면 멈추지 못하게 해서 쓰게 한다.
- 파일 수정 전: HUMAN.md, NOTES.md, `docs/spec.md`, `tools/`, `.codex/` 수정을 막는다. `apply_patch`, 셸 리다이렉트, `tee`, `sed -i`, `perl -pi`, `mv`, `cp`·`rsync`(폴더에 넣기 포함), `rm`·`unlink`(폴더째·glob), 편집기(`vim`, `ed` 등), `patch`·`git apply`, `find -delete`·`-exec rm`, `git rm/mv/checkout/restore`, `bash -c` 안의 명령, `env`·`sudo`·`nohup`·`xargs`로 감싼 명령을 본다. `git reset --hard`, `stash`, `clean`은 보호 문서에 커밋 안 된 변경이 있을 때만 막는다. 검증 에이전트는 `docs/verify/` 밖에 쓰지 못한다(에이전트 이름이 hook 입력에 담길 때만 걸린다).
- guard가 못 잡는 것: `cd tools && ...`처럼 폴더를 옮긴 뒤 쓰기, `python -c` 같은 다른 언어로 쓰기, `ln`, `dd`, `chmod`, 같은 명령 안에서 만든 패치 파일, `$(...)`로 만든 경로. 실수 방지용이지 완전한 차단이 아니다. HUMAN.md, NOTES.md, docs/spec.md는 쓰자마자 커밋해 두면 git으로 되살릴 수 있다.

## 쓰는 법
```bash
git clone https://github.com/ahnjamin/codex-hackathon-kit ~/kit
sh ~/kit/setup.sh .
python3 -m venv .venv && . .venv/bin/activate   # macOS는 전역 pip 설치가 막혀 있을 수 있다
pip install -r requirements.txt
sh tools/gate.sh
python3 tools/check-hooks.py
codex --search          # venv를 켠 셸에서. --search가 있어야 웹 검색이 된다
```
명세서(`docs/spec.md`)는 다른 세션에서 만들어 이 폴더에 저장한다.

**Codex를 연 첫 1분에 확인할 것**
- `/hooks`에서 이 폴더의 hook을 신뢰한다. 신뢰 전에는 경고 없이 hook이 하나도 돌지 않는다(guard도, HANDOFF 강제도). 목록에 SessionStart, UserPromptSubmit, PreToolUse, Stop 넷이 보이면 된다.
- 메시지를 하나 보내 `[시간]` 줄이 붙는지 본다. 안 붙으면 hook이 안 도는 것이다.

화면 e2e 테스트를 쓰려면(선택) 사람이 미리 설치한다. 웹 IDE에서 막히면 건너뛴다. 검증은 TestClient 테스트와 사람이 써 보기로 대신한다.
```bash
pip install playwright && python -m playwright install chromium
```

## 플러그인과 MCP
플러그인은 따로 설치하지 않는다. 대회 웹 IDE에서 마켓플레이스 설치가 될지 모르고, 플러그인 안의 쓸 만한 것은 대부분 스킬이라 `library/`에 담아 두었다.
- superpowers 전체는 넣지 않았다. `using-superpowers`가 모든 작업을 자기 절차로 끌고 가서 AGENTS.md 흐름과 부딪힌다. 필요한 스킬만 골라 담았다.
- 브라우저·화면 조작(browser, chrome, computer-use, Playwright MCP)은 대회의 Computer Use 금지에 걸릴 수 있어 뺐다. AI는 브라우저를 직접 조작하거나 스크린샷을 보고 판단하지 않는다. e2e는 단언하는 테스트 코드(webapp-testing)나 HTTP 요청으로 하고, 눈으로 보는 확인은 사람이 한다.
- 웹 검색은 MCP 대신 `codex --search`로 켠다.
- MCP를 하나 쓴다면 라이브러리 문서 검색용 context7. 원격 주소라 npm이 필요 없다. Codex 설정(`~/.codex/config.toml`) 형식은 아래와 같다. 웹 IDE의 MCP 설정 JSON 형식은 그날 화면을 보고 옮긴다. 대회 망에서 접속되는지는 확인하지 않았다.
```toml
[mcp_servers.context7]
url = "https://mcp.context7.com/mcp"
```

## 설계 메모
- 에이전트는 둘이다. 명세서는 별도 Codex 세션에서 만들어 오므로 스펙 에이전트는 두지 않고, 구현(`implementer`)과 검증(`verifier`)만 나눈다. 구현한 쪽이 자기 결과를 검증하지 않게 하려는 것이다. 큰 작업 안에서는 서브에이전트를 더 불러도 된다.
- 큰 작업은 개수와 작업별 시간 상한을 정하지 않는다. 3시간 안에 완성하는 것이 기준이고, 모자라면 시연에 안 보이는 기능부터 뺀다.
- 큰 작업이 끝나면 검증(e2e, 다크 패턴)과 사람이 직접 써 보기, 객관식 퀴즈 5문항, NOTES.md 메모가 이어진다.
- 작업 목록은 TASKS.md 표 하나로 관리한다.
- 세션은 큰 작업 단위로 넘긴다. 작업이 끝나면 HANDOFF.md를 쓰게 강제하고, 새 세션이 열리면 hook이 읽혀 준다.
