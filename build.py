"""Builds locales/tr.json from source/tr.json.

Each source entry holds the English original and the Turkish translation.
Short labels are shown as "Turkish (English)"; long sentences stay Turkish only,
so menus keep Orca's original name visible without doubling paragraph length.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
MAX_BILINGUAL_WORDS = 4
SENTENCE_PUNCTUATION = re.compile(r'[.:;!?…]\s*$|[.!?]\s')


TRAILING_ELLIPSIS = re.compile(r'(\.\.\.|…)$')


def is_short_label(english: str) -> bool:
    english = TRAILING_ELLIPSIS.sub('', english)
    return (
        bool(english)
        and len(english.split()) <= MAX_BILINGUAL_WORDS
        and not SENTENCE_PUNCTUATION.search(english)
    )


def render(english: str, turkish: str, keyword: bool = False) -> str:
    if keyword:
        # Search keywords keep the English word so typing either language still matches; Orca also
        # shows some of these as labels, so the English goes in parentheses like any short label.
        return turkish if english.casefold() == turkish.casefold() else f'{turkish} ({english})'
    if not is_short_label(english) or english.casefold() == turkish.casefold():
        return turkish
    # Menu items like "Check for Updates..." keep their ellipsis on the Turkish side only.
    return f'{turkish} ({TRAILING_ELLIPSIS.sub("", english)})'


def main() -> None:
    source = json.loads((ROOT / 'source' / 'tr.json').read_text(encoding='utf-8'))
    tree: dict = {}
    for key, entry in source.items():
        node = tree
        *parents, leaf = key.split('.')
        for part in parents:
            node = node.setdefault(part, {})
        node[leaf] = render(entry['en'], entry['tr'], entry.get('keyword', False))
    (ROOT / 'locales' / 'tr.json').write_text(
        json.dumps(tree, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    print(f'{len(source)} strings written')


if __name__ == '__main__':
    main()
