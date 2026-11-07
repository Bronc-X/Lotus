# Repository audit — 2026-09-25

A full read of the tree at `9ea203f` (main, merged 2026-09-08) on branch
`claude/happy-albattani-10pwxj`, plus every check the repository ships.
Findings are ordered by how much they cost a user or maintainer today, not by
how hard they are to fix. Each one names the file and, where useful, the line.

## What was run

| Check | Result |
|---|---|
| `python scripts/validate_repo.py` (after installing `requirements-validation.lock`) | Steps 1–17 pass. Step 18 (unit tests): 1,347 run, **1 error**, 64 skipped. See finding 2. |
| Relative link, image and heading-anchor check over all 130 Markdown files | 0 broken targets, 0 unresolved anchors, 40 distinct external URLs (not fetched) |
| `python scripts/language_coverage.py` | `stale_review_required` for all six languages. See finding 5. |
| `python scripts/source_registry_check.py --enforce-freshness` | Passes; warns `review_scope: partial` and `last_verified` 18 days old |
| Whitespace hygiene (trailing spaces, tabs, CRLF, missing final newline) | Clean across every tracked text file |
| `TODO` / `FIXME` / `XXX` markers | None outside the quarantined archive |
| GitHub state | CI green on `main` (validate-seedance-skill run 1143). One open PR (#205). Seven open issues, two substantive (#206, #110). |

The design audit, masthead generator check, schema execution, vocabulary
schema, project-state, continuity, behavior-contract, sequence-eval,
generation-run, prompt-lint, architecture-stress, eval-harness and
frame-extraction self-tests all pass. Nothing below changes that; the problems
are in the places the checks do not look.

## A. Costs a user today

### 1. Open issue #206: the ZIP import into Claude fails on two filenames

[Issue #206](https://github.com/Emily2040/seedance-2.0/issues/206) (2026-09-14,
unanswered) reports `Zip file contains path with invalid characters` when
importing the repository into Claude. Exactly two tracked paths contain
characters outside `A–Z a–z 0–9 . _ / -`:

```text
assets/fonts/BodoniModa[opsz,wght].ttf
assets/fonts/BodoniModa-Italic[opsz,wght].ttf
```

The square brackets and comma are Google Fonts' variable-font naming. The
installer excludes `assets/fonts/`, so `install_codex_skill.py` users never see
this, but the README's own front page says "Download ZIP also works" and that
path ships the fonts. This is the most likely cause; it is not confirmed
against Claude's importer, and the issue has not been asked for a file list.

Fix: rename both files to bracket-free names (for example
`BodoniModa-VF.ttf`, `BodoniModa-Italic-VF.ttf`), then update the font paths in
`scripts/build_masthead_outlines.py`, the provenance record in
`assets/masthead-outlines.json`, and the tests in `tests/test_build_hero.py`
that name them. Re-run `python -I -S -B scripts/build_masthead_outlines.py --check`
to prove the committed geometry is unchanged. Reply on the issue.

### 2. The validation suite fails on a common developer Python layout

`tests/test_build_hero.py:551`
(`test_in_venv_sitecustomize_cannot_short_circuit_a_check`) errors with:

```text
SystemExit: masthead build environment config does not match trusted base Python
```

Cause: in this container `python3` is a symlink in a different directory from
the real binary (`/usr/local/bin/python3 → /usr/bin/python3.11`). `venv` writes
`home = /usr/local/bin` into `pyvenv.cfg`; `require_trusted_venv_config` in
`scripts/build_masthead_outlines.py:766` compares that directory to the parent
of the resolved base executable, `/usr/bin`, and refuses. GitHub's
`setup-python` has no cross-directory symlink, so CI is green. Homebrew,
pyenv shims, Debian `alternatives` and many container images do have one, and
`build_masthead_outlines.py --install-build-deps` will refuse on those machines
for the same reason.

Fix: compare interpreter identity rather than directory equality. Resolve
`home/python<major>.<minor>` (or `home/python`) and the trusted base executable
and require `os.path.samefile`, keeping the version and
`include-system-site-packages` checks as they are. Add a regression that
creates the venv through a symlinked interpreter.

### 3. Tests write into the repository root

- `tests/test_extract_frame_output_policy.py:32` sets its temporary root to
  `<repo>/work` and leaves the empty directory behind after a run (present
  after this audit's run). It is not in `.gitignore`.
- `tests/test_prompt_lint.py:47` and `:646` create `prompt-lint-test-*`
  directories in the repository root. They are removed on success and left on
  a crash. Also not ignored.

Fix: add `work/` and `prompt-lint-test-*/` to `.gitignore`, or move both under
a single ignored `.seedance-test-tmp/` root. The Windows-sandbox reason for an
in-repo temp root is documented in the test; keep it, just ignore it.

## B. Facts that disagree with each other

### 4. The package says 6.7.0; its own metadata says 6.6.0

| File | Says |
|---|---|
| `SKILL.md` | `version: "6.7.0"` |
| `evals/evals.json` | `"version": "6.6.0"` |
| `evals/generation-benchmark.json` | `"benchmark_version": "6.6.0"` |
| `V6_SEQUENCE_PROMPT_COMPILER_MANIFEST.md:5` | "Active package version: `6.6.0`" |
| `V6_SEQUENCE_PROMPT_COMPILER_MANIFEST.md:8` | "Current expected eval cases: 126" (the suite has 140) |

`docs/v6-release-readiness.md` requires "eval metadata … must agree with
`metadata.version`", and `tests/test_release_docs_consistency.py` checks the
READMEs but not these files. Either bump them or add them to the version test.
The `schema_version: "6.6.0"` values in `examples/*/project-state.json` may be
deliberate schema versioning; if so, say so in `references/json-schema.md`.

### 5. The language-coverage contract has been stale for every language since 2026-09-07

`evals/language-coverage.json` snapshots were taken at `39f3543` (2026-09-07).
Every quickstart and every vocabulary file has changed since, so
`language_coverage.py` reports `stale_review_required` for en, zh, ja, ko, es
and ru. `docs/LANGUAGE_COVERAGE.md` says a flag is cleared only by a recorded
review, never by re-hashing. Eighteen days later no review is recorded. The
README's "Evidence status" still reads as though the contract were merely
pending, not stale.

### 6. The README's platform paragraph lags its own reference

`README.md:344-346` says other-surface availability of the newer model line
"remained unconfirmed in the 2026-08-01 review" and quotes provider inventories
"as of 2026-06-20". `references/api-status.md` now opens with a 2026-09-07
scoped update stating that Runway's API catalog documents `seedance2_5`
separately and that the older wording "must not be read as a current claim".
The front page still makes the older claim. `tests/test_release_docs_consistency.py`
pins the phrase "unconfirmed", so the wording has to change with the test.

### 7. Source registry is `review_scope: partial` and drifting

`references/source-registry.md:3-4`: `last_verified: 2026-09-07`,
`review_scope: partial`. The scheduled Monday job has kept
[issue #155](https://github.com/Emily2040/seedance-2.0/issues/155) open since
2026-08-17. Not a defect, but an owed human task that will block
`validate_repo.py --release` at day 30 (2026-10-07).

### 8. Seven weeks of "Unreleased" changes, including a compatibility break

`CHANGELOG.md` "Unreleased" has accumulated since the 2026-08-05 hardening
pass. It includes closing the root of `take-review.schema.json` with
`additionalProperties: false` and rejecting `accepted_deviations` on a
rejected take. Anyone installing from `main` gets behaviour the v6.7.0 release
note does not describe, under the v6.7.0 label. Cut 6.7.1 (or 6.8.0 if the
schema change is judged breaking) or label `main` as pre-release in the README.

### 9. One action, two pins, three workflows

`actions/checkout` is pinned to `11d5960a…` (v4.4.0) in the Linux job of
`validate-skills.yml` and in `privileged-frame-publication.yml`, but to
`11bd7190…` (v4.2.2) in the Windows job of the same file and in
`source-freshness-review.yml`. Both are valid; the point of SHA pinning with a
tracking comment is one answer per action.

### 10. Owner identity strings do not match the GitHub account

`.github/CODEOWNERS:4` comments "Iamemily2050 (@iamemily2050)" while every rule
uses `@Emily2040`; `LICENSE:3` says "Iamemily2050 (@iamemily2050)"; the README
footer says "Emily / Iamemily2050" linking to `github.com/Emily2040`.
`@iamemily2050` is not the account that owns the repository. Pick one public
name and one handle.

### 11. Three different positionings and a brand colour that is not the brand

- GitHub repository description: "Comprehensive production pipeline for
  quad-modal AI filmmaking with Seedance 2.0".
- `agents/openai.yaml`: "Professional Seedance video prompting", and
  `brand_color: "#0EA5E9"` (sky blue).
- `README.md`: "an agent skill for planning shots, binding references and
  continuing from an accepted clip."
- `references/frontend-design-system.md`: one accent, amber `#E2A75E` /
  `#A86F24`, "never a second hue".

The README sentence is the good one. Align the other three to it.

### 12. The design documents contradict the README and each other

- `references/frontend-design-system.md` design goals: "No collapsed
  Markdown" and "Validation commands visible above the fold after the skill
  map". The README uses four `<details>` blocks and validation is collapsed.
- `docs/frontend-redesign.md` (the acceptance doc) assumes collapsed optional
  sections. The two design documents disagree.
- `docs/v6-release-readiness.md` requires "a visible multilingual start
  section". It is inside a collapsed `<details>` (`README.md:505-530`).
- `README.md:858` says the operating diagram `skill-map.svg` is served through
  a `prefers-color-scheme` picture element. `README.md:375` embeds it as a
  plain Markdown image.

### 13. The README breaks its own 500-character line rule

`references/frontend-design-system.md` README rules: "No line longer than 500
characters." `README.md:206` is 580 characters. No check enforces the rule.

## C. Front-page quality (input to the redesign plan)

These are the findings that motivate `docs/README_REDESIGN_PLAN.md`; the plan
carries the fixes.

### 14. The front page is a maintainer manual with a reader path stapled to the top

870 lines, 8,304 words, 69 KB. Roughly half is maintainer material: installer
durability semantics (`fsync`, `0700` workspaces, ACLs), the masthead venv
trust chain, ledger inode handling. The Install `<details>` runs about 1,000
words of that before the client table a reader actually opened it for.

### 15. "Read in your language" does not go to the language pages

`README.md:15` links each language to its quickstart. The full pages
`docs/README.zh.md`, `docs/README.ja.md`, `docs/README.ko.md` are reachable
only from inside collapsed details (Workflow Index rows, Multilingual Start).

### 16. The three CJK pages are one template in three languages

| | zh | ja | ko |
|---|---|---|---|
| Words | 75 | 82 | 134 |
| H2 sections | 5, same order | 5, same order | 5, same order |
| Routing table | 6 rows, same rows | same | same |
| Example | product bottle, water drop, warm side light | same scene | same scene |
| Images | 0 | 0 | 0 |
| Links | 1 (to its quickstart) | 1 | 1 |
| Bare backtick paths that should be links | 6 | 6 | 6 |
| English field labels inside the localized prompt | no | `Camera:` / `Sound:` lines | `Camera:` / `Sound:` lines |

The English page is 8,304 words. Each of these pages introduces itself as "not
a translation" and then is exactly that: a shared skeleton with the nouns
swapped. This is the core of the redesign brief.

### 17. No Spanish or Russian page

Declared in `docs/LANGUAGE_COVERAGE.md` and pinned by
`tests/test_language_coverage.py` (`readme` must be `null` for es/ru). Adding
them is a contract change, not just two files.

### 18. The masthead cannot be localized with the current font

- The READS strip mixes scripts and codes: `EN · 中文 · 日本語 · 한국어 · ES · RU`.
- CJK in that strip is live monospace text; readers get whatever CJK fallback
  their system has, which is the platform-dependent rendering the outlined
  type was adopted to end.
- The vendored Bodoni Moda (checked from its `cmap`: 428 glyphs) has Spanish
  diacritics and `¿ ¡ «` but **no Cyrillic and no CJK**. A localized outlined
  tagline needs a second OFL face per script.

### 19. Duplicated content on one page

Quickstart links appear three times; the four language rows appear in both the
Workflow Index and Multilingual Start; "Final hardening contract" restates
`docs/RELEASE_v6.7.0.md`, which the design system says belongs in the changelog.

### 20. Heading case and structure

Sentence case and Title Case alternate ("Start Here", "Choose a workflow",
"Evidence status", "What This Skill Does", "Operating System At A Glance").
Thirteen H2 headings live inside `<details>`, so GitHub's outline lists
sections whose jump links land on collapsed content. Three spaced hyphens
stand in for dashes where the rest of the page uses em dashes.

### 21. Locale register slips

- `docs/QUICKSTART.es.md` states no regional variant is validated, then uses
  the Spain spelling `vídeo` six times and `« »` guillemets. Neutral Spanish
  for the Americas is `video` and `" "`. Choose and declare.
- `docs/QUICKSTART.ru.md` is consistent (ё throughout, «ёлочки», formal вы);
  one `идет` without ё.
- `docs/README.ko.md` uses ASCII colons in prose, which is correct Korean
  typography; the zh and ja pages use full-width. Correct, but worth stating
  in a style note so a future editor does not "fix" it.

## D. Weight and hygiene

### 22. 18 MB of PNGs for a text skill, nine of them archive-only

Ten PNGs of 1.5–2.4 MB each; nine appear only in `docs/visual-archive.md`.
`scripts/validate_skills.py` `REQUIRED_FILES` lists all of them, so they cannot
be moved to a release asset or LFS without changing the validator. The pack is
25 MB. This matters most for the Chinese audience, for whom GitHub clones are
slow; the redesign plan proposes a mirror and a ZIP-first install path.

### 23. `.gitattributes` does not declare `*.ttf`

It marks gif/jpeg/jpg/png/webp binary. Git's heuristic handles TTF, but the
file's own comment says "Never touch binary assets"; declare it.

### 24. No contribution surface, and the issue tracker shows it

No `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue template or PR template. The
README invites contribution through "open issues". Of seven open issues, four
are one-word or empty (#58 "film", #89, #157 "Seedance", #158 "update") and
[#110](https://github.com/Emily2040/seedance-2.0/issues/110), a Chinese user
asking for 2.5 support on 2026-07-31, has no reply although the README now
answers the question. Add templates, close the empties, answer #110 in Chinese
with a link to the 2.0/2.5 boundary.

### 25. One open PR

[#205](https://github.com/Emily2040/seedance-2.0/pull/205)
(`codex/editorial-brief-traceability`, 2026-09-08) is unrelated to this audit
and still open.

## Suggested order

1. Rename the two font files and reply to #206 (finding 1).
2. Fix the venv trust comparison (2) and ignore the test temp roots (3).
3. Bump the 6.6.0 metadata and eval-case count, and pin them in the version
   test (4).
4. Rewrite the README platform paragraph with the 2026-09-07 boundary and update
   its test (6); align the action pins (9), identity strings (10) and brand
   colour (11).
5. Record the language review or explicitly re-baseline with rationale (5);
   complete or retire the partial registry scope before 2026-10-07 (7).
6. Cut a release so `main` and "v6.7.0" mean the same thing (8).
7. Then execute `docs/README_REDESIGN_PLAN.md`, which resolves 12–21.

Nothing in this audit was changed in the tree; this document and the plan are
the only additions.
