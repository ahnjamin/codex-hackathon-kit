# 스킬 보관함

Codex는 이 폴더를 자동으로 읽지 않는다. 과제에 필요한 것만 작업 폴더로 꺼낸다.
```bash
cp -r ~/kit/library/<분야>/<스킬> .agents/skills/
```
꺼낸 뒤 Codex를 다시 열면 읽힌다. 세션마다 스킬 설명이 맥락에 들어가니 한꺼번에 많이 꺼내지 않는다.
스킬 지침이 AGENTS.md 흐름(TASKS.md, gate, verifier, HANDOFF)과 부딪히면 AGENTS.md를 따른다.

## 작업 폴더에 기본으로 깔리는 것 (`templates/.agents/skills/`)
| 스킬 | 쓰는 때 | 출처 |
|---|---|---|
| brainstorm | 무엇을 만들지 정할 때, spec이 애매할 때 | 직접 만듦(superpowers brainstorming 줄임) |
| quiz | 큰 작업 끝, 객관식 5문항 | 직접 만듦 |
| web-recipes | FastAPI + 정적 HTML + SQLite 조각 | 직접 만듦 |
| webapp-testing | Playwright e2e 테스트 코드(단언만, AI가 스크린샷으로 판단하지 않음) | anthropics/skills |
| frontend-design | 화면을 만들 때 디자인 방향 | anthropics/skills |
| systematic-debugging | 버그, 실패하는 테스트 | obra/superpowers |
| test-driven-development | 테스트 먼저 쓰기 | obra/superpowers |
| verification-before-completion | `끝`이라고 하기 전 확인 | obra/superpowers |

## 보관함
| 분야 | 스킬 | 쓰는 때 |
|---|---|---|
| frontend | nextjs | Next.js App Router로 가야 할 때 |
| frontend | react-best-practices | React 성능·구조 점검 |
| frontend | shadcn | shadcn/ui 컴포넌트 |
| backend | ai-sdk | 서비스 안에 AI 기능. 대회 규칙 확인 먼저, Vercel 계정이 필요한 부분은 못 씀 |
| backend | auth | 로그인이 필수인 과제. Clerk 등 외부 계정이 필요한 부분은 못 씀 |
| engineering | diagnosing-bugs | systematic-debugging으로 안 잡히는 버그 |
| engineering | prototype | 방향이 둘일 때 빠르게 비교 시안 |
| engineering | domain-modeling | 데이터 구조가 복잡한 과제 |
| engineering | code-review | 마감 전 코드 리뷰 |
| engineering | research | 레퍼런스 조사 단계 |
| process | brainstorming | 원본(긴 버전). 시간이 넉넉할 때만 |
| process | writing-plans | 큰 작업 하나가 너무 클 때 하위 단계 정리(파일로 쓰지 않음) |
| process | dispatching-parallel-agents | 서로 안 겹치는 하위 작업 병렬 |
| process | requesting-code-review, receiving-code-review | 리뷰 요청·반영 |
| product | onboarding, signup | 첫 사용 흐름, 가입 화면 |
| product | cro, copywriting, copy-editing | 랜딩·버튼 문구 |
| product | pricing, popups, marketing-psychology | 가격표, 팝업, 설득 문구(다크 패턴 주의) |
| product | ab-testing, analytics | 실험·지표가 과제에 있을 때 |
| tokens | caveman | 답을 짧게 해 토큰 아끼기. 사람 설명이 필요한 퀴즈·NOTES 안내 때는 끈다 |
| tokens | ponytail | 가장 짧게 되는 코드. 켜 두면 테스트·설명까지 줄이니 테스트·퀴즈·커밋 메시지에는 적용하지 않는다 |
| tokens | ponytail-review, ponytail-audit | 과하게 짠 코드 찾기 |
| own | plain-writing | README·발표 문구에서 AI 말투 빼기 |
| own | site-check | 제출 전 사이트 버그·취약점 점검(고치지 않고 보고, curl만 씀) |
| own | clean-ui-style | 깔끔한 화면 스타일 |

## 출처와 라이선스
각 스킬 폴더에 원본 LICENSE를 같이 넣었다.
| 출처 | 라이선스 | 가져온 버전 |
|---|---|---|
| https://github.com/anthropics/skills (webapp-testing, frontend-design) | Apache-2.0 | 2026-10-30 main |
| https://github.com/obra/superpowers | MIT | 7.0.0 |
| https://github.com/mattpocock/skills | MIT | 1.3.1 |
| https://github.com/vercel/vercel-plugin | Apache-2.0 | 0.50.0 |
| https://github.com/coreyhaines31/marketingskills | MIT | 2.8.12 |
| https://github.com/DietrichGebert/ponytail | MIT | 4.10.0 |
| https://github.com/JuliusBrussee/caveman | Apache-2.0 (NOTICE 포함) | 2026-10-30 main |
| own/, brainstorm, quiz, web-recipes, 키트 나머지 | MIT (최상위 LICENSE) | |

## 키트가 바꾼 것
- 몇몇 스킬 맨 위에 `> **키트에서 쓸 때**` 문단을 덧붙였다(대회 규칙과 AGENTS.md 흐름에 맞추려고): process/*, engineering/research·domain-modeling·prototype·code-review, backend/*, frontend/nextjs, product/pricing·popups·marketing-psychology.
- vercel 스킬의 `upstream/` 폴더(원본 사본)는 지웠다. 꺼내면 스킬이 둘로 잡혀서다. nextjs 링크는 `references/`로 고쳤다.
- 원본에 있는데 여기 없는 파일을 가리키던 링크(analytics의 tools 목록, copywriting의 seo-audit 참조, caveman README의 형제 스킬)는 설명으로 바꿨다.
- systematic-debugging의 `superpowers:` 접두 이름을 뺐다.
- own/site-check에서 브라우저 조작, gstack `/cso`, 홈 폴더 기록을 뺐다.

넣지 않은 것: anthropics/skills의 docx·pdf·pptx·xlsx(재배포 불가 라이선스), gstack 계열(전용 바이너리 필요), 브라우저·화면 조작 플러그인(대회 Computer Use 금지), 라이선스 파일이 없는 스킬.
