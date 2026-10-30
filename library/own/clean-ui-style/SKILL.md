---
name: clean-ui-style
description: "무채색 바탕에 색을 아껴 쓰는 깔끔한 웹 UI 디자인 규칙. 다크·라이트 모드와 포인트 색 하나를 골라 쓴다(서체, 글자 크기 단계, 여백 표, 모서리 둥글기 공식, 배경 색 목록, 아이콘 세트, 움직임 곡선, 상태 디자인). elayadesign/ai-design-skills의 landing-page-design에서 디자인 규칙(Part B)만 떼어 한국어 화면에 맞게 고친 것. 사용자가 \"clean-ui-style로\", \"클린 스타일\", \"그 랜딩 스킬 톤앤매너로\", \"이 스타일로 만들어줘\"라고 할 때 쓴다. 랜딩페이지 구성이나 문구 전략에는 쓰지 않는다. 사용자가 다른 디자인 스킬(frontend-design, impeccable)을 지정하면 그쪽을 따른다."
---

# Clean UI Style

어떤 화면(서비스 화면, 대시보드, 설정, 목록, 소개 페이지)에도 쓰는 시각 규칙이다. 모든 시각 값은 아래 규칙에서 골라야 하고 즉석에서 지어내지 않는다. 사용자의 명시적인 요청이 규칙과 부딪히면 사용자를 따른다.

## 시작 전에: 모드와 포인트 색 고르기

사용자가 정하지 않았으면 만들기 전에 한 번만 묻는다. 정했으면 묻지 않는다.

1. **모드:** 다크 또는 라이트. 둘 다 지원해야 하면 두 모드 모두 목록 색으로 만들고 `prefers-color-scheme`으로 바꾼다.
2. **포인트 색:** 한 가지. 사용자가 브랜드 색을 주면 그 색을 쓴다. 없으면 후보 몇 개를 실제 버튼 모양으로 보여 주고 고르게 한다.

**포인트 색 규칙**
- 포인트 색은 하나뿐이다. 두 번째 포인트 색을 만들지 않는다.
- 쓰는 곳: 주요 버튼, 링크, 선택·현재 위치 표시, 포커스 링, 진행 표시. 넓은 면(배경, 섹션 바탕, 카드 바탕)에는 쓰지 않는다.
- 버튼 글자와 포인트 색, 포인트 색 글자와 배경은 명도 대비 4.5:1 이상. 모자라면 포인트 색의 명도만 조절한다.
- hover는 같은 색을 조금 밝게(다크) 또는 어둡게(라이트) 한다. 새 색을 만들지 않는다.
- 성공·경고·오류 색은 포인트 색과 별개로 상태 표시에만 쓴다.

**글자 색**
- 다크: 본문 `#EDEDED`, 보조 `#A1A1A1`
- 라이트: 본문 `#171717`, 보조 `#666666`

## 한국어 화면 조정 (원본 규칙보다 우선)

- **서체:** 라틴 문자는 Geist, 한글은 Pretendard. 둘을 한 font-family 스택으로 묶어 한 서체처럼 쓴다. 이 조합은 "한 사이트 한 서체" 규칙 위반으로 보지 않는다.
  `font-family: "Geist", "Pretendard Variable", Pretendard, -apple-system, "Apple SD Gothic Neo", sans-serif;`
  Pretendard CDN: `https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css`
- **줄바꿈:** 한글 본문과 제목에 `word-break: keep-all`을 같이 준다. 외톨이 단어 규칙(B1)은 한글에서도 지킨다.
- **문장 대소문자 규칙(B8 sentence case)** 은 영어 문구에만 적용한다.
- **실제 서비스의 숫자와 후기:** B8의 "그럴듯한 이름과 숫자를 지어내라"는 시안·목업에서만 쓴다. 실제로 운영하는 서비스 화면에는 없는 사용자 수, 후기, 고객사를 지어내지 않는다. 데이터가 없으면 그 칸을 빼거나 빈 상태로 둔다.
- **피해야 할 한국어 상투어:** 혁신적인, 차원이 다른, 획기적인, 손쉽게 누구나, 새로운 경험을 선사합니다. 제품이 하는 일을 평범하게 말한다.
- **B5 히어로 규칙** 은 화면 맨 위 큰 제목이 있을 때만 쓴다. 서비스 화면에는 그런 제목이 없을 수 있다.
- **B10 출시 체크리스트** 는 공개 웹사이트를 처음부터 만들 때만 확인한다. 화면 하나나 컴포넌트를 만들 때는 건너뛴다.

---

# PART B — Visual system

Every visual value must resolve through these rules instead of being invented ad hoc.

## B1. Typography

### Fonts

**Use:** Geist, Manrope, Geist Mono, Poppins.

**Never use:** Inter, Roboto, Arial, Open Sans, Helvetica.

**Never use italic fonts** anywhere in the interface.

**One typeface per site.** Do not pair two fonts unless the prompt explicitly asks for it. Geist Mono is allowed alongside a primary font only for code, data, or numeric UI where a monospace is functionally required.

**Never use ultra bold weights** (900 / black). Cap at semibold or bold.

### Copy rules

**No hyphens in text.** Do not use `-` inside body copy, headings, or labels. Rewrite the phrase instead.

**No orphaned words.** A single word must never sit alone on the last line. Apply `text-wrap: balance` for headings and `text-wrap: pretty` for body copy.

### Type scale

Always resolve font sizes to Tailwind's default type scale. Never leave arbitrary values in place, including `text-[19px]`, `font-size: 22px`, or `1.4rem`.

If an existing size does not land exactly on a step, snap it to the **closest step below**, taking both the size and its paired line height.

| Class | Size | Line height |
|---|---|---|
| `text-xs` | 12px (0.75rem) | 16px |
| `text-sm` | 14px (0.875rem) | 20px |
| `text-base` | 16px (1rem) | 24px |
| `text-lg` | 18px (1.125rem) | 28px |
| `text-xl` | 20px (1.25rem) | 28px |
| `text-2xl` | 24px (1.5rem) | 32px |
| `text-3xl` | 30px (1.875rem) | 36px |
| `text-4xl` | 36px (2.25rem) | 40px |
| `text-5xl` | 48px (3rem) | 1 |
| `text-6xl` | 60px (3.75rem) | 1 |
| `text-7xl` | 72px (4.5rem) | 1 |
| `text-8xl` | 96px (6rem) | 1 |
| `text-9xl` | 128px (8rem) | 1 |

Do not combine scale snapping with independently set custom line heights elsewhere in an audit. Tracking and line height may only be adjusted **within** the value the matched step already provides, so the two rules never fight each other.

### Button type

- Main buttons: `text-base` (16px), semibold.
- Smaller header buttons: `text-sm` (14px), semibold.

## B2. Spacing

Only these values. Nothing between them, nothing outside them.

| Token | Value |
|---|---|
| Spacing-0 | 0 |
| Spacing-25 | 2px |
| Spacing-50 | 4px |
| Spacing-75 | 8px |
| Spacing-100 | 12px |
| Spacing-200 | 16px |
| Spacing-300 | 24px |
| Spacing-400 | 32px |
| Spacing-500 | 40px |
| Spacing-600 | 48px |
| Spacing-700 | 64px |
| Spacing-800 | 80px |
| Spacing-900 | 96px |

**Main buttons:** 8px vertical padding, 12px horizontal padding.

## B3. Corner radius

Only use Tailwind's radius values.

**Nested radius formula.** When a shape sits inside another shape and the gap between them is **less than 32px**:

```
inner radius = outer radius − gap
```

Apply this only when the result is **greater than 2**. Below that, leave the inner shape square or unchanged.

Example: an outer card at `rounded-2xl` (16px) with 8px of internal padding gives an inner element an 8px radius (`rounded-lg`).

## B4. Borders and backgrounds

- **Never apply a border to only one side of a card.** Borders go all the way around or not at all.
- **Never use gradients in backgrounds.** Backgrounds are flat.

### Dark mode background colors

Use only these:

`#000000` · `#181818` · `#1F1F1F` · `#272727` · `#313131` · `#131209`

### Light mode background colors

(원본에 없어 이 스킬에서 더함) Use only these:

`#FFFFFF` · `#FAFAFA` · `#F5F5F5` · `#EFEFEF` · `#E5E5E5`

## B5. Hero section

### Heading color

- **Dark theme:** left to right gradient on the heading text, `#FFFFFF` → `#9B9B9B`.
- **Light theme:** left to right gradient on the heading text, `#000000` → `#666666`.

This is the one place gradients are used, and only on text, never on the background.

### Layout

- Heading and subheading both get a **max width of 680px**.
- Read the heading copy and insert line breaks at **meaningful** points.
- Never break a line in a way that cuts a phrase awkwardly or makes the sentence harder to read. Break where the thought breaks.

## B6. Icons

**Use:** Phosphor, Solar, or Iconamoon.

**Never use:** Material Icons, Material Symbols.

## B7. Motion

Motion should feel weighted and decelerate into place. Never ship a browser default curve (`ease`, `linear`, `ease-in-out`).

**Base curve:** `ease-[cubic-bezier(0.22,1,0.36,1)]` with `duration-500` for layout and position changes. Color and opacity shifts on hover may use `duration-300`, never shorter than 200ms.

Animate only `transform` and `opacity`. Never animate `top`, `left`, `width`, or `height`.

Respect `prefers-reduced-motion`: replace movement with a plain opacity change.

### Navigation

**Resting state.** A compact bar that floats off the top edge rather than sitting flush against it, centered and sized to its content. It uses a translucent surface over a background blur so page content stays faintly visible behind it. Spacing comes from B2, radius from B3.

**Menu toggle.** The open and close icon transforms between its two states instead of swapping instantly. Use an icon from B6 or draw the lines yourself; either way the change is animated with the base curve.

**Mobile menu.** Opens as a full height panel, not a small dropdown. The panel background uses the theme's base surface at high opacity with a strong blur.

**Link entrance.** Links inside the open menu arrive one after another in reading order, each moving up a short distance (Spacing-300, 24px) while fading in. Step each item 60ms after the previous one and cap the total sequence at 400ms so long menus never feel slow.

### Scroll reveals

Sections entering the viewport rise a short distance (Spacing-400, 32px) and fade from 0 to full opacity over 600 to 800ms on the base curve. Reveal each section once; do not replay on scroll back up.

Trigger reveals with `IntersectionObserver` or Framer Motion's `whileInView`. Never attach work to an unthrottled `window.addEventListener('scroll')`, since it runs on every frame and drags down mobile performance.

---

## B8. Content realism

Every piece of sample content should read like it came from a real product with real users.

- **Write the copy.** No placeholder Latin, no "Your headline here". Draft real sentences in the product's voice.
- **People.** Give testimonials and team members full, specific names that fit the product's audience and region. Never reuse one face for two people.
- **Brands and logos.** Invent names that sound like they belong in the product's industry. A logistics tool's customers sound like logistics companies, not generic tech startups.
- **Numbers.** Avoid suspiciously round figures. Pricing should look like real pricing, metrics should carry a decimal or an odd final digit, and dates across a list should vary.
- **Banned filler words.** Do not write "revolutionize", "supercharge", "cutting edge", "effortless", "transform your workflow", "take it to the next level", "harness the power", or "world class". Say what the product does in plain terms instead.
- **Sentence case** for headings and buttons.
- **System messages.** Confirmations are calm and specific ("Invoice sent to Dana"). Errors say what failed and what to do next ("Upload failed. The file is over 20 MB."). No cute interjections, no exclamation marks.

## B9. States

Every interactive element ships with its full state set:

- **Hover** — background shift, slight scale, or translate
- **Active** — `scale(0.98)` or `translateY(1px)` for physical feedback
- **Focus** — a visible focus ring. Accessibility requirement, not optional.
- **Loading** — skeleton loaders shaped like the real layout, not circular spinners
- **Empty** — a composed "getting started" view, never a blank panel
- **Error** — inline and specific. Never `window.alert()`.

No dead links. A button pointing at `#` is either linked or visually disabled. The current page must be indicated in the navigation.

## B10. Ship requirements

Things that get forgotten and make a page feel unfinished:

- Privacy policy and terms links in the footer
- A custom, branded 404
- Client side form validation for email format and required fields
- A skip to content link for keyboard users
- Cookie consent where the jurisdiction requires it
- A branded favicon
- `<title>`, meta description, `og:image`, and social sharing tags
- Alt text on every meaningful image
- Semantic HTML: `<nav>`, `<main>`, `<article>`, `<aside>`, `<section>`
- A way back from every page


---

# 체크리스트

- [ ] 서체는 Geist + Pretendard 스택 하나, 이탤릭 없음, 900 굵기 없음
- [ ] 글자 크기는 모두 Tailwind 단계, 여백은 모두 여백 표 값
- [ ] 안쪽 모서리는 공식(바깥 − 간격)대로
- [ ] 카드 한쪽만 테두리 없음, 배경 그라데이션 없음, 배경은 모드별 목록 색만
- [ ] 포인트 색은 하나, 좁은 곳에만, 대비 4.5:1 이상
- [ ] 아이콘은 Phosphor, Solar, Iconamoon 중 하나
- [ ] 모든 전환은 B7 곡선, transform과 opacity만 움직임, reduced-motion 대응
- [ ] hover, active, focus, loading, empty, error 상태 모두 있음
- [ ] 죽은 링크 없음, 현재 위치 표시
- [ ] 실제 서비스면 지어낸 숫자·후기 없음

---

## 출처와 라이선스

원본: [elayadesign/ai-design-skills](https://github.com/elayadesign/ai-design-skills) `skills/landing-page-design/SKILL.md`의 PART B(B1~B10)를 그대로 옮겼다. 랜딩 전략(PART A), 태그라인 섹션(B11), 출력 형식은 뺐고, "모드와 포인트 색 고르기", 라이트 배경 색 목록, "한국어 화면 조정"을 더했다. 2026-10-28에 가져옴.

원본 스킬의 일부는 [taste-skill](https://github.com/Leonxlnx/taste-skill)(Leon Lin, MIT)에서 가져와 다시 쓴 것이다.

<details>
<summary>ai-design-skills license</summary>

```
MIT License

Copyright (c) 2026 Elaya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
</details>

<details>
<summary>taste-skill license</summary>

```
MIT License

Copyright (c) 2026 Leonxlnx

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
</details>
