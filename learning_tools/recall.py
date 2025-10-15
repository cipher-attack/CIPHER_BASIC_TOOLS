from __future__ import annotations
import os
import re
import json
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Iterable, Dict, Any


@dataclass
class RecallCard:
    id: str
    question: str
    answer: str
    interval_days: int = 0
    repetition: int = 0
    ease_factor: float = 2.5
    due: str | None = None


def _sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def _iter_markdown_files(path: str) -> Iterable[str]:
    if os.path.isdir(path):
        for root, _dirs, files in os.walk(path):
            for name in files:
                if name.lower().endswith(".md"):
                    yield os.path.join(root, name)
    else:
        if path.lower().endswith(".md"):
            yield path


_QA_BLOCK_RE = re.compile(r"^Q:\s*(.+)$", re.IGNORECASE)
_ANS_BLOCK_RE = re.compile(r"^A:\s*(.+)$", re.IGNORECASE)


def extract_cards_from_markdown(markdown_text: str) -> List[RecallCard]:
    lines = markdown_text.splitlines()
    cards: List[RecallCard] = []

    i = 0
    while i < len(lines):
        q_match = _QA_BLOCK_RE.match(lines[i].strip())
        if q_match:
            question = q_match.group(1).strip()
            answer_lines: List[str] = []
            i += 1
            # If next line starts with A:, prefer that as answer; otherwise collect until blank line
            if i < len(lines) and _ANS_BLOCK_RE.match(lines[i].strip()):
                answer = _ANS_BLOCK_RE.match(lines[i].strip()).group(1).strip()  # type: ignore
                i += 1
            else:
                while i < len(lines) and lines[i].strip() != "":
                    answer_lines.append(lines[i])
                    i += 1
                answer = "\n".join(answer_lines).strip()
            if answer:
                card_id = _sha1(question + "\n\n" + answer)
                cards.append(RecallCard(id=card_id, question=question, answer=answer))
            continue
        # Heuristic: headings with '?' become question; next paragraph is answer
        if lines[i].lstrip().startswith(("#", "##", "###", "####", "#####", "######")) and "?" in lines[i]:
            question = re.sub(r"^#+\s*", "", lines[i]).strip()
            # Collect next paragraph
            i += 1
            answer_lines: List[str] = []
            while i < len(lines) and lines[i].strip() == "":
                i += 1
            while i < len(lines) and lines[i].strip() != "":
                answer_lines.append(lines[i])
                i += 1
            answer = "\n".join(answer_lines).strip()
            if answer:
                card_id = _sha1(question + "\n\n" + answer)
                cards.append(RecallCard(id=card_id, question=question, answer=answer))
            continue
        i += 1

    return cards


def generate_from_markdown(input_path: str, output_path: str) -> int:
    all_cards: List[RecallCard] = []
    for md_file in _iter_markdown_files(input_path):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError:
            continue
        all_cards.extend(extract_cards_from_markdown(text))

    # Load existing deck if present to merge without duplicating identical IDs
    existing: Dict[str, Any] = {"cards": []}
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except OSError:
        pass
    existing_ids = {c.get("id") for c in existing.get("cards", [])}

    merged = list(existing.get("cards", []))
    for c in all_cards:
        if c.id not in existing_ids:
            merged.append(asdict(c))

    out = {"cards": merged}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(merged)} cards to {output_path} (added {len(merged) - len(existing.get('cards', []))}).")
    return 0
