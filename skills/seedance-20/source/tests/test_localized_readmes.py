"""Structural contracts for the six language front pages.

Each page is written for its reader rather than translated, so these tests do
not compare pages to each other. They protect the parts every page must share:
the language switcher, the active version string, real links instead of bare
paths, a first example written in the page's own language, a review-status
disclosure, and lines that stay readable on GitHub.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PAGES = {
    "en": "README.md",
    "zh": "docs/README.zh.md",
    "ja": "docs/README.ja.md",
    "ko": "docs/README.ko.md",
    "es": "docs/README.es.md",
    "ru": "docs/README.ru.md",
}
NAMES = {
    "en": "English",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어",
    "es": "Español",
    "ru": "Русский",
}
ORDER = ("en", "zh", "ja", "ko", "es", "ru")
LATIN_FIELD_LABELS = re.compile(r"^(?:Camera|Sound|Light|Style|Constraint)\s*:", re.MULTILINE)
BARE_ROUTE = re.compile(r"(?<!\[)`(?:\.\./)?(?:skills|references)/[^`\n]*\.md(?:#[^`\n]*)?`")


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def active_version() -> str:
    match = re.search(r'^  version:\s*["\']([^"\']+)["\']\s*$', read("SKILL.md"), re.MULTILINE)
    if not match:
        raise AssertionError("SKILL.md metadata.version is missing")
    return match.group(1)


def first_text_block(text: str) -> str:
    match = re.search(r"```text\n(.*?)\n```", text, re.S)
    if not match:
        raise AssertionError("page has no fenced text example")
    return match.group(1)


def link_target(from_page: str, to_page: str) -> str:
    source = Path(PAGES[from_page]).parent
    target = Path(PAGES[to_page])
    if source == Path("."):
        return target.as_posix()
    if target.parent == source:
        return target.name
    return ("../" / target).as_posix()


class LanguageSwitcherTests(unittest.TestCase):
    def test_every_page_names_all_six_languages_in_the_shared_order(self) -> None:
        for code, relative in PAGES.items():
            switcher = next(
                (line for line in read(relative).splitlines()
                 if all(NAMES[other] in line for other in ORDER)),
                None,
            )
            with self.subTest(page=relative):
                self.assertIsNotNone(switcher, "page has no line naming all six languages")
                positions = [switcher.index(NAMES[other]) for other in ORDER]
                self.assertEqual(positions, sorted(positions))

    def test_every_page_links_every_other_full_page(self) -> None:
        for code, relative in PAGES.items():
            text = read(relative)
            for other in ORDER:
                if other == code:
                    continue
                with self.subTest(page=relative, to=other):
                    self.assertIn(f"]({link_target(code, other)})", text)


class SharedFactsTests(unittest.TestCase):
    def test_pages_carry_the_active_version(self) -> None:
        version = active_version()
        for relative in PAGES.values():
            with self.subTest(page=relative):
                self.assertIn(f"v{version}", read(relative))

    def test_pages_disclose_review_status_and_link_the_coverage_record(self) -> None:
        for code, relative in PAGES.items():
            text = read(relative)
            target = "docs/LANGUAGE_COVERAGE.md" if code == "en" else "LANGUAGE_COVERAGE.md"
            with self.subTest(page=relative):
                self.assertIn(f"]({target})", text)

    def test_no_line_exceeds_the_design_system_limit(self) -> None:
        for relative in PAGES.values():
            for number, line in enumerate(read(relative).splitlines(), start=1):
                with self.subTest(page=relative, line=number):
                    self.assertLessEqual(len(line), 500)


class ReaderLanguageTests(unittest.TestCase):
    def test_repository_paths_are_links_not_bare_code_spans(self) -> None:
        for code, relative in PAGES.items():
            if code == "en":
                continue
            with self.subTest(page=relative):
                self.assertEqual(BARE_ROUTE.findall(read(relative)), [])

    def test_cjk_first_examples_carry_no_latin_field_labels(self) -> None:
        for code in ("zh", "ja", "ko"):
            block = first_text_block(read(PAGES[code]))
            with self.subTest(page=PAGES[code]):
                self.assertIsNone(LATIN_FIELD_LABELS.search(block))

    def test_japanese_and_korean_pages_do_not_use_the_chinese_tag_family(self) -> None:
        for code in ("ja", "ko"):
            with self.subTest(page=PAGES[code]):
                self.assertNotIn("@图片1", read(PAGES[code]))

    def test_spanish_pages_use_the_declared_neutral_spelling(self) -> None:
        for relative in ("docs/README.es.md", "docs/QUICKSTART.es.md"):
            text = read(relative)
            with self.subTest(page=relative):
                self.assertNotIn("vídeo", text)
        self.assertIn("video", read("docs/README.es.md"))

    def test_russian_page_writes_yo_consistently(self) -> None:
        text = read("docs/README.ru.md")
        self.assertIn("ё", text)
        self.assertIsNone(re.search(r"\b(?:еще|идет|берет|учет|свое)\b", text))


if __name__ == "__main__":
    unittest.main()
