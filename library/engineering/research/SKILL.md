---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

> **키트에서 쓸 때**(codex-hackathon-kit이 덧붙임): 조사 결과는 따로 파일을 만들지 않고 `docs/refs.md` 표에 적는다. 웹 검색은 `codex --search`로 연 세션에서만 된다. 완성된 앱을 통째로 가져오는 후보는 적지 않는다(대회 규칙).


Spin up a **background agent** to do the research, so you keep working while it reads.

Its job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.
