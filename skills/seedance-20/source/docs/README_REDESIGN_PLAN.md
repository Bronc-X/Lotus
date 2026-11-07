# README redesign plan: six front doors, one house

Status: proposal, 2026-09-25. Companion to `docs/REPO_AUDIT_2026-09-25.md`.
Nothing here is implemented yet; the plan is written so each phase can land
as its own pull request with the validators still green.

## The brief

The repository has one front page written for an English reader and three
short pages that share a single skeleton with the nouns swapped. The audit
(findings 14–21) shows the result: a 8,300-word English page, three 75–134 word
pages, no Spanish or Russian page, and a masthead that cannot say anything in
four of the six scripts it lists.

The redesign principle is **commission, don't translate.** Each language gets
its own page, built for how that reader actually arrives, scans, decides and
distrusts. The pages share facts (version, licence, evidence status, the tag
rule, the safety posture, the review-status disclosure) and share the house
style (one left spine, hairlines, one amber mark, outlined display type, no
badges, no costume). Everything else — order, density, register, example
scene, typography, what goes above the fold — is decided per language.

"Highest taste" is not decoration. For each reader it means: the page answers
their first question in their first screen, in their own punctuation, with an
example they would have written themselves, and never claims more than the
repository can show.

## What must survive (constraints from the validators)

The repository pins a lot of the front page. A redesign that breaks these
fails CI; the plan works inside them.

| Surface | Pinned by | Constraint |
|---|---|---|
| `README.md` order | `tests/test_readme_reader_path.py` | `## Start Here` before `## Install` before `## Validation`; literal `<summary>Installation by client, replacement and recovery details</summary>`; no `assets/hero-command-center.png` |
| First fenced `text` block | same test, `tests/test_teaching_art.py` | The paper-fan prompt: every line ≤ 32 characters; contains "The fan settles on the wood." and "No music."; the prose before `<!-- teaching-image:placement -->` still names the action and endpoint |
| Teaching image | `tests/test_teaching_art.py` | `assets/paper-fan-teaching.png`, its caption and `docs/PAPER_FAN_ART.md` link stay between the `installed-readme-gallery` markers, inside the Start Here → Choose a workflow span |
| Language links | `scripts/design_audit.py` | All six `docs/QUICKSTART*.md` links present; `#start-here` and `#install` resolve; every image local, alt-texted, PNG/SVG only; ≤ 4 MiB of embedded assets counting both masthead themes |
| Validation headings | `tests/test_validation_contract.py`, `tests/test_strict_cli_contract.py` | `## Validation` … `### Git checkout-only hygiene` … `### Checked-in source metadata age` … `## Design Standard`, in that order |
| Validation commands | same tests, `tests/test_python_support_contract.py` | `python scripts/validate_repo.py --release` before the Git subsection; `git diff --check` only inside it, with "requires Git metadata" and "Do not run it in a Download ZIP extraction"; the two CPython range sentences; `--strict` only on behavioral scripts |
| Install table rows | `tests/test_client_install_guidance.py` | The Google Antigravity and Hermes Agent rows keep their exact path guidance |
| Model-line paragraph | `tests/test_release_docs_consistency.py` | Both primary 2.5 URLs, the phrase pattern "exact … launch … unconfirmed", "live on Dreamina", no "coming soon", no dated strings the test forbids |
| Installed copy | `scripts/install_codex_skill.py` | Only the `installed-readme-gallery` and `installed-readme-validation` marker regions are rewritten for the installed payload; everything else ships verbatim |
| `docs/README.zh.md`, `.ja.md`, `.ko.md` | `tests/test_release_docs_consistency.py`, `validation/install-payload.txt` | Must contain `v6.7.0` (the active version string); they are shipped in the installed payload, so they cannot embed source-only images |
| es / ru pages | `tests/test_language_coverage.py`, `evals/language-coverage.json`, `docs/LANGUAGE_COVERAGE.md` | Today `readme` must be `null` for es and ru; adding pages is a contract change (test, JSON and table together) |
| Every page | `scripts/content_audit.py`, `scripts/vocab_schema_check.py` public-claim lint, `tests/test_client_install_guidance.py` | No stale-status phrases, no studio-style examples, no claim that static checks establish language quality, no unguarded Hermes/Antigravity path variants |

Three mechanics have to be built before the language pages can be finished;
they are in the "Shared mechanics" section. The English restructure and the
Chinese page can start before them.

## English — `README.md`

**Reader.** Arrives from a GitHub search, a Codex or Claude Code skill list, or
a link in a thread. Skims. Wants to know in one screen what this is, whether it
is safe to install, and what one prompt looks like. Distrusts adjectives,
badges, and anything that reads like a launch post. Comfortable with tables and
progressive disclosure. Reads on a phone as often as not.

**Taste.** The design system already names it: a call sheet. Dense, precise,
undecorated, one left spine. The current page has the right first screen and
then loses the reader in maintainer internals. The redesign is subtraction.

**Architecture (target ≈ 260 lines above the collapsed material, ≈ 2,500 words total).**

1. Masthead (unchanged geometry).
2. One sentence the masthead does not say. Keep the current one.
3. Four jump links, then the quiet facts line (version · licence · changelog ·
   author).
4. **Languages line, promoted and repointed.** Native-script names in the
   reader's own order, each to its *full page*:
   `English · 中文 · 日本語 · 한국어 · Español · Русский`. The six quickstart
   links move to a "5-minute quickstart" sentence directly under it so
   `design_audit.py` still finds them.
5. `## Start Here` — exactly as now (pinned).
6. `## Choose a workflow` — as now.
7. `## Install` — the three-line clone/install, then the client table
   *visible*, then the pinned `<details>` containing only: the two-step
   walkthrough and a single link to a new `docs/INSTALL_INTERNALS.md` that
   receives the durability, `fsync`, ACL and named-stream prose verbatim.
8. `## Evidence status` — as now, with the language bullet corrected to name
   the stale-review state honestly.
9. `## What it routes` — one table merging today's Workflow Index and Skill
   Map (situation → skill → output). No prose paragraphs. Reference library
   moves to `docs/REFERENCE_INDEX.md`.
10. `## Model line and platform facts` — three sentences with the pinned 2.5
    boundary, rewritten to the 2026-09-07 scope, and one link to
    `references/api-status.md`. The provider inventory paragraph leaves the
    front page.
11. `## Validation` — keep the pinned headings and commands; move the
    evaluator, ledger and masthead trust essays (≈ 2,600 words) to
    `docs/VALIDATION.md` and `docs/MASTHEAD_BUILD.md`, leaving one paragraph
    each with a link. The section stays inside a `<details>` only if the
    design system's "no collapsed Markdown" goal is formally retired in the
    same PR (audit finding 12); otherwise it is a short visible section.
12. `## Design Standard` — five sentences and two links.
13. Changelog · License.

**Typography and voice.** Sentence-case headings throughout. Em dashes only;
remove the three spaced hyphens. Straight quotes in prose; keep the curly
quotes only inside the "user says" table cells, where they mark speech. No
line over 500 characters (add the check to `design_audit.py`). No emoji. No
exclamation marks. Every table has a one-line lead-in that says what decision
it serves.

**Example.** Keep the paper fan. It is pinned, it is good, and it is the one
scene every other page will *not* reuse.

## 中文 — `docs/README.zh.md`

**Reader.** 即梦 / 剪映 / 豆包 users first, then Volcengine/Ark developers,
then MCN and e-commerce short-video teams. Many read on a phone inside WeChat;
many reach GitHub slowly or through a mirror. Chinese prompt culture is
concrete and pattern-driven: readers collect 模板, compare 效果, and judge a
page by whether it gives them something they can paste in the next minute.

**Taste.** Density is respect. A Chinese reader is comfortable with a longer,
tighter page than a Japanese reader, more tables, more numbered steps, and a
direct imperative voice (不要 / 必须 / 先…再…). What they distrust is empty
elevation — 高级感, 电影感, 氛围感 — which is exactly the anti-slop rule the
vocabulary already teaches, so the page can practise what it preaches. They
scan by heading and table, not by paragraph. They want the platform's own
words: 即梦, 首帧 / 尾帧, 运镜, 景别, 光位, `@图片1`, 简繁.

**Architecture (target ≈ 1,400 字).**

1. 标题与一句话 — `Seedance 2.0 Skill OS · 中文` and one line: 把一个想法写成一条可以直接提交的导演级提示词。
2. 语言切换行 (shared component).
3. **先看这里** — one copyable Chinese prompt with 为什么这样写 (four bullets: 一个动作、一个终点、一台固定机位、一个明确的声音决定), and the unrendered-example disclosure in one sentence.
4. **三步上手** — 下载 → 安装 → 调用, each one command. Add a 国内下载 note: GitHub 慢时用 Download ZIP; if a Gitee mirror is created, link it here (proposal, not yet existing).
5. **按情况选路** — table: 你现在有什么 → 先打开 → 你会得到什么, six rows, every path a real link.
6. **中文提示词六条规则** — the existing five plus 简繁与字幕分开决定.
7. **参考素材与 `@图片1`** — the two tag families (`@图片1` vs `@Image1`) never mixed in one prompt; role per asset.
8. **连续剧情** — the template, then the seven-step loop in Chinese.
9. **中文美学语域怎么落地** — a short table from `references/vocab/zh.md`: 烟火气 / 国风水墨 / 武侠 / 废土, each with the physical elements that produce it. This section exists only on the Chinese page.
10. **安全改写** — 明星脸、品牌、歌曲、真人声音 → 原创等价物; state that translating a blocked request into another language is not a repair.
11. **常见问题** — three answers: 2.0 与 2.5 的边界 (this answers issue #110 in the reader's language), 为什么字幕不让模型生成, 安装了但客户端没显示怎么办.
12. **审核状态** — AI-assisted draft, independent Chinese review pending, link to `LANGUAGE_COVERAGE.md`. Version string present.

**Typography.** 全角标点 (，。：；！？「」) in prose; half-width inside code and
paths. A space between 中文 and Latin/numbers ("在 GitHub 上", "v6.7.0 的").
Headings 4–8 characters, verb-led. Simplified script for the page; state that
a Traditional page is not provided and that the prompt script is the user's
choice. No bold walls: bold one phrase per section at most.

**Example scene (烟火气, unrendered).**

```text
夜市摊位，固定中景。摊主把一勺热油浇在铁板上，
白汽腾起，遮住他半张脸，再慢慢散开。
灯泡在头顶晃了一下就停。
声音：油的滋滋声、远处人声、结尾一声铁铲刮板。
无配乐，无字幕。最后两秒保持白汽散尽后的画面。
```

Why this scene: it is a register the Chinese vocabulary already names, it is
physical (steam, oil, a swinging bulb), it has a visible endpoint, and it is not
a product bottle.

## 日本語 — `docs/README.ja.md`

**Reader.** Individual creators, small 映像制作会社, anime-adjacent and VTuber
creators (the 2D grammar reference matters to them first), agency planners.
Habits formed on Qiita and Zenn: a page earns trust through 丁寧さ, a real 目次,
explicit 前提条件 and 注意事項, and by never overstating.

**Taste.** Precision over volume; whitespace over density. A Japanese reader
is put off by imperative 命令形, by a page that hides costs or risks, and by
誇張. They expect the conventional order (概要 → 特徴 → 前提条件 →
インストール → 使い方 → 注意事項) and read caveats as competence, not
hedging. Figures and short lists beat wide tables. The dialogue register
system (文体) and the aesthetic registers (間, 侘び寂び, もののあわれ, 幽玄, 粋)
are things a Japanese reader will look for and be quietly pleased to find
treated seriously.

**Architecture (target ≈ 1,600 字).**

1. タイトルと一文 — `Seedance 2.0 Skill OS · 日本語` and: 思いついた場面を、そのまま提出できる演出付きプロンプトにします。
2. 言語切り替え行.
3. **目次** (GitHub renders the outline, but a written 目次 is expected).
4. **概要** — three sentences: what it is, what it is not (生成はしません), what it costs (費用は生成サービス側).
5. **できること** — three items, no more.
6. **前提条件** — Python 3.11–3.13, a supported client, and the note that reference tags stay Latin (`@Image1`; `@画像1` は使いません).
7. **インストール** — one command, one confirmation command, one 注意 box about `--force`.
8. **はじめの一歩** — the localized prompt with 狙い (intent) in four lines and the unrendered disclosure.
9. **使い方** — table by situation, six rows, real links, polite verbs.
10. **日本語プロンプトの作法** — tags, 文体 of dialogue, endpoint, sound, 字幕は後処理.
11. **連続クリップ** — template and the loop.
12. **アニメ・2D の場合** — the only page with this section above the fold; three rules from `references/2d-anime-grammar.md` (レイヤー、動きの緩急、レンズ語彙を使わない).
13. **注意事項** — 権利 (実在の人物・キャラクター・楽曲), 費用, 未検証の範囲, in a `> [!NOTE]`-style block written in です・ます体.
14. **関連資料** — four links.
15. **レビュー状況** — AI 草稿、独立レビュー未完了, link, version string.

**Typography.** です・ます体 throughout; requests as 〜してください. 「」 for
quotes, 、。 punctuation, 中黒 「・」 for inline lists. Decide the 全角/半角
spacing rule once and apply it (the quickstart currently inserts spaces,
"v6.7.0 の日本語"; either keep that consistently or remove it consistently;
recommendation: keep, it matches Zenn house style). No English field labels
inside a Japanese prompt: カメラ / 光 / 音 are in `references/vocab/ja.md`.
Headings are nouns (概要、前提条件), not verbs.

**Example scene (間, unrendered).**

```text
縁側、固定のミディアムショット。
老いた手が風鈴の短冊を指で止め、そのまま離す。
短冊がひと揺れして止まるまで、カットしない。
木漏れ日が板の間でゆっくり形を変える。
音：風鈴が一度だけ鳴り、あとは蝉の声のみ。
台詞なし、音楽なし。最後の二秒は静止を保つ。
```

Why this scene: it stages 間 physically (a held frame, one sound, then
nothing), uses 木漏れ日 from the vocabulary as-is, has a clear endpoint, and
reads as something written in Japanese rather than about Japan.

## 한국어 — `docs/README.ko.md`

**Reader.** 유튜브 쇼츠 and 릴스 creators, 광고 대행사 and 프로덕션 teams,
웹드라마 and 뮤직비디오 makers, and a developer community for whom GitHub is a
first-class reading surface. Korean readers move fast, want 빠른 시작 at the
top, and respond to well-placed callouts. They are exposed daily to
variety-show 자막 culture, so "the model does not write your subtitles" needs a
Korean-specific explanation, not a rule.

**Taste.** Practical, warm, direct. Consistent 합니다체 for body text with
〜하세요 in steps (matching the quickstart); never mix 해요체 into the same
page. Avoid 번역투: "〜에 대한", stacked passives, "〜되어지다". Standard
외래어 표기 (프롬프트, 클립, 카메라); use 참조 in prose and note 레퍼런스 as
the spoken form once. Korean punctuation is ASCII (`:` `,` `"`), which the
current page gets right; a style note should say so. Light structure markers
are welcome in Korean READMEs; within this house style use GitHub `> [!TIP]`
and `> [!IMPORTANT]` blocks rather than emoji.

The two things a Korean reader will specifically care about: **말투** (speech
level) in dialogue, which the vocabulary already treats properly, and
**실존 인물 초상권** — idol and actor likeness is the single most common unsafe
request from this audience, so the safety section moves up and speaks plainly.

**Architecture (target ≈ 1,300 자).**

1. 제목과 한 줄 — `Seedance 2.0 Skill OS · 한국어` and: 떠오른 장면을 바로 제출할 수 있는 연출 프롬프트로 만듭니다.
2. 언어 전환 줄.
3. **빠른 시작** — 3단계, each one command, in a numbered list with a `> [!TIP]` about restarting the client.
4. **첫 프롬프트** — localized prompt, 의도 in four bullets, unrendered disclosure.
5. **상황별 안내** — table, six rows, real links.
6. **실존 인물·브랜드·음원** — moved up: idol/actor likeness, K-pop 음원, brand logos → 원작 기능을 유지한 대안; a sentence that switching languages does not make a blocked request acceptable.
7. **한국어 프롬프트 원칙** — tags stay Latin (`@Image1`, `@이미지1` 아님), 말투 for dialogue, endpoint, sound, 자막은 편집에서 (with the variety-show explanation).
8. **연속 클립** — template and loop.
9. **한국적 정서를 화면으로** — 한 / 정 / 여백의 미 / 신명 / 사극 from `references/vocab/ko.md`, each as physical elements.
10. **자주 묻는 질문** — 2.0과 2.5, 설치 확인, 자막.
11. **검토 상태** — AI 초안, 독립 검토 대기, link, version string.

**Typography.** Spaces between 한글 and Latin/numbers ("v6.7.0 버전", "Claude
Code에서" follows the 붙여쓰기 rule for particles). Big quotes `" "` for
speech. Headings are short noun phrases. Tables keep one idea per cell.

**Example scene (정, unrendered).**

```text
포장마차 안, 고정 미디엄 숏.
주인이 말없이 어묵 국물 한 컵을 손님 앞으로 밀어 준다.
김이 올라와 손님의 안경을 잠깐 흐리고, 손님이 안경을 벗는다.
백열등 하나가 두 사람을 비춘다.
소리: 국물 끓는 소리, 비닐 천막에 떨어지는 빗소리. 대사 없음, 음악 없음.
마지막 2초는 안경을 내려놓은 손에서 멈춘다.
```

Why this scene: 정 is shown as a small act of care, not narrated; the steam on
the glasses gives a visible micro-event and endpoint; nothing in it is a
product or a celebrity.

## Español — new `docs/README.es.md`

**Reader.** Creators and agencies across the Americas and Spain, mostly
bilingual with English tooling terms, reading on desktop and phone. Spanish
readers accept longer sentences but not longer pages, and want the *why*
stated alongside the *what*. They notice regional register immediately.

**Taste.** Warm and direct, tuteo, neutral Spanish for the Americas as the
declared default: `video` (not `vídeo`), `computadora` or `equipo` (not
`ordenador`), no `vosotros`, straight `" "` quotes rather than `« »`. The
quickstart currently mixes registers (audit finding 21); the page and the
quickstart declare the same choice. Inverted `¿ ¡` always. Examples drawn from
shared Hispanic visual culture without postcard clichés: una sobremesa, un
taller de cerámica, una plaza al atardecer — never mariachi or flamenco as
shorthand.

**Architecture (target ≈ 1,200 palabras).**

1. Título y una frase — `Seedance 2.0 Skill OS · Español` y: Convierte una idea en un prompt dirigido, listo para enviar.
2. Línea de idiomas.
3. **Empieza aquí** — prompt localizado, "por qué estas decisiones" en cuatro viñetas, aviso de ejemplo sin renderizar.
4. **Instalación** — un comando, una comprobación.
5. **Elige tu camino** — tabla de seis filas con enlaces reales.
6. **Reglas para prompts en español** — etiquetas intactas (`@Image1`), diálogo exacto (tuteo/voseo/usted lo decide el personaje, no el documento), punto final visible, sonido explícito, subtítulos en posproducción.
7. **Continuación** — plantilla y bucle.
8. **Seguridad** — personas reales, marcas, canciones → equivalentes originales; cambiar de idioma no repara un pedido bloqueado.
9. **Estado de revisión** — borrador asistido por IA, revisión independiente pendiente, variante regional declarada (neutro americano), enlace, versión.

**Masthead.** Bodoni Moda covers `ñ á é í ó ú ¿ ¡` (verified), so the existing
outline toolchain renders a Spanish tagline without a second face:
"Dirige al modelo. No microgestiones el cuadro."

**Contract change.** `evals/language-coverage.json` `languages.es.readme`
becomes `docs/README.es.md`; `tests/test_language_coverage.py` drops the
`assertIsNone` for es; `docs/LANGUAGE_COVERAGE.md` row updated;
`validation/install-payload.txt` gains the path.

**Example scene (sobremesa, unrendered).**

```text
Sobremesa, plano medio fijo desde la cabecera de la mesa.
Una mujer mayor parte una naranja con las manos y le da la mitad al niño de al lado.
El niño la huele antes de morderla.
Luz de tarde por la ventana izquierda; migas y una taza vacía en primer plano.
Sonido: cubiertos lejanos, una silla que cruje, sin música ni diálogo.
Los dos últimos segundos se quedan en la cáscara sobre el mantel.
```

## Русский — new `docs/README.ru.md`

**Reader.** Developers and motion designers with Habr and Telegram habits,
studio producers, ad agencies. Direct, technically literate, allergic to
marketing, and reassured by explicit limits. This audience will read a section
called "Что не проверено" before anything else, which fits the repository's
evidence posture exactly.

**Taste.** Formal «вы» in lowercase, «ёлочки» for quotes, spaced em dash
(«кадр — это»), ё written consistently (the quickstart already does; keep it),
sentence-case headings, precise nouns (кадр, план, монтаж, референс as
accepted jargon), tables with exact limits and dates. No exclamation marks, no
diminutives, no "просто". Long paragraphs are fine if they are dense; padding
is not.

**Architecture (target ≈ 1,300 слов).**

1. Заголовок и одна фраза — `Seedance 2.0 Skill OS · Русский`: Превращает идею в срежиссированный промпт, готовый к отправке.
2. Строка языков.
3. **Что это и чего это не делает** — three sentences; the last says it does not generate and does not pay.
4. **Начните здесь** — localized prompt, "почему так" in four bullets, unrendered disclosure.
5. **Установка** — one command, one check.
6. **Выберите путь** — table, six rows.
7. **Ограничения и что не проверено** — moved up for this reader: no rendered pilot, no independent Russian review, the 2.0/2.5 boundary with dates.
8. **Правила для промпта на русском** — tags stay Latin, exact dialogue verbatim, ты/вы is the character's choice, endpoint, sound, subtitles in post.
9. **Продолжение** — template and loop.
10. **Безопасность** — real people, brands, music → original equivalents.
11. **Статус проверки** — AI draft, independent review pending, link, version.

**Masthead.** Bodoni Moda has no Cyrillic (verified). Options: (a) keep the
Latin wordmark, which Russian readers expect for a product name, and outline
only the Cyrillic tagline and eyebrow from an OFL didone with Cyrillic
coverage — Playfair Display or Prata — subset to the glyphs used; (b) live
Cyrillic in the monospace strip only. Recommendation: (a). The tagline:
«Режиссируйте модель. Не управляйте каждым кадром».

**Contract change.** Same as Spanish for `ru`.

**Example scene (unrendered).**

```text
Кухня в хрущёвке, статичный средний план.
Мужчина ставит чайник на плиту и ждёт, не отходя.
Когда чайник начинает свистеть, он снимает его до того, как свист станет громким.
Свет из окна слева, зимний, серый; на подоконнике замёрзшее стекло.
Звук: гул газа, короткий свист, тиканье часов. Без музыки, без реплик.
Последние две секунды — рука на ручке чайника, пар уходит вверх.
```

## Shared mechanics

### 1. The language switcher

One line, identical position on every page (directly under the one-sentence
description), native-script names in this fixed order:
`English · 中文 · 日本語 · 한국어 · Español · Русский`. Each name links to that
language's *full page*; the current page is plain text. Quickstart links stay
one line below on `README.md` (design audit) and in the footer elsewhere.

### 2. Localized mastheads

The wordmark `Seedance 2.0 Skill OS` stays Latin on every page: it is the
product name and the one thing all six pages share visually. The **eyebrow,
tagline and specification strip** are localized. The spec strip's third field
becomes the *current* language's name in its own script rather than a list of
six, which removes the mixed `EN · 中文 · ES` problem.

Because live text must stay monospace (design system) and the display serif
has no CJK or Cyrillic, the localized tagline is outlined like the wordmark:

| Page | Display face for the tagline | Coverage check |
|---|---|---|
| en, es | Bodoni Moda (existing) | Verified: Latin + Spanish diacritics |
| ru | Playfair Display or Prata (SIL OFL) | Both ship Cyrillic; choose after a print test at 26 px |
| zh | Source Han Serif SC / Noto Serif SC (SIL OFL) | Subset to the tagline glyphs only |
| ja | Source Han Serif JP / Noto Serif JP | Same |
| ko | Source Han Serif KR / Noto Serif KR | Same |

Implementation: `scripts/build_masthead_outlines.py --lang xx` shapes one
tagline string per language and records font, version, OFL notice and glyph
subset in `assets/masthead-outlines.json`; `scripts/build_hero.py --lang xx`
writes `assets/hero-{lang}-dark.svg` and `assets/hero-{lang}-light.svg` from
the same geometry. Subset TTFs of a sentence are 20–80 KB; commit them beside
the existing fonts with bracket-free names (audit finding 1). Extend
`design_audit.py` to audit every `hero-*.svg` under the same editorial rules
and to include localized pages' embedded assets in a per-page 1 MiB budget.

The localized READMEs ship in the installed payload; SVGs of ≈ 45 KB are cheap
to add to `validation/install-payload.txt`, so the pages can embed their
masthead without extending the installer's marker rewrite. PNG teaching art
stays on `README.md` only.

### 3. Page-level tests, one per language

Add `tests/test_localized_readmes.py`:

- every page has the language switcher line with all six names, in order;
- the version string `v6.7.0` (derived from `SKILL.md`, not hard-coded);
- the first fenced `text` block contains no Latin field labels (`Camera:`,
  `Sound:`) on zh/ja/ko pages and no `@图片1` on ja/ko pages;
- every `skills/…` or `references/…` mention is a link, not a bare code span;
- no line over 500 characters;
- es page contains `video` and not `vídeo`; ru page contains no `е`-for-`ё`
  in a small list of common words;
- a stated review-status sentence and a link to `LANGUAGE_COVERAGE.md`.

### 4. Coverage and review

Each page ends with the same three facts in its own language: AI-assisted
draft; independent review by a reviewer for the declared locale (zh-CN Hans,
ja-JP, ko-KR, es neutral Americas, ru-RU) pending; link to the coverage record.
`docs/LANGUAGE_COVERAGE.md` gains the es and ru rows and a "page architecture
differs by design" sentence so a future reviewer does not report the pages as
"out of parity". The existing concept IDs (REF-ROLE, STATE-OBSERVED,
ACTION-ENDPOINT, CONTROL-OWNER, DIALOGUE-EXACT, AUDIO-MODE, USER-CHOICE,
SPEND-BOUNDARY) are the review checklist for every example scene above; each
scene was written to exercise ACTION-ENDPOINT and AUDIO-MODE explicitly.

No page may say it was reviewed until the evidence artifact says so.

## Rollout

| Phase | Lands | Validators to run | Acceptance |
|---|---|---|---|
| 0 | Audit fixes 1–4, 9–11 (fonts renamed, venv check, temp roots ignored, version metadata, pins, identity, brand colour) | `validate_repo.py`, `build_masthead_outlines.py --check` | Suite green on a symlinked Python; issue #206 answered |
| 1 | English restructure; the four new `docs/` pages that receive the moved material; design docs reconciled (finding 12); 500-char check | `design_audit.py` and the seven README tests named in the constraints table | Front page ≤ 300 lines before the last section; every pinned string present; manual 390/768/1280 px light/dark pass recorded per `docs/frontend-redesign.md` |
| 2 | Chinese page | `vocab_schema_check.py`, `content_audit.py`, new localized test | Reviewed by a zh-CN reader for register and punctuation before merge; issue #110 answered with a link |
| 3 | Japanese page | same | ja-JP reader sign-off on 文体 consistency and the 2D section |
| 4 | Korean page | same | ko-KR reader sign-off on 말투 consistency and the likeness section |
| 5 | Spanish and Russian pages; coverage contract, test and payload manifest updated | `language_coverage.py`, `test_language_coverage`, `test_install_payload` | Declared variants stated on page and in the coverage table |
| 6 | Localized mastheads; `build_hero.py --lang`; design audit extension | `build_hero.py --check`, `design_audit.py` | Six masthead pairs byte-reproducible from the generator; subset fonts with OFL notices committed |
| 7 | Independent review recorded in `evals/multilingual-native-review-evidence.json` (scope extended by a reviewed change first) | `test_multilingual_native_review` | Pages may then drop the "pending" line |

Phases 2–5 are independent of each other and of phase 6; a page ships with
the Latin masthead until its localized pair exists.

## What this plan deliberately does not do

- It does not translate the English page. The English page gets shorter; the
  others get written.
- It does not add a Traditional Chinese, Latin American versus Castilian, or
  Ukrainian page. Each is a separate commission with its own reviewer; the
  coverage table should list them as "not provided", as it does today for
  es/ru.
- It does not claim any page reads as written by a first-language editor
  until the evidence record says so. The example scenes above are authored
  drafts for that reviewer to correct, not finished copy.
