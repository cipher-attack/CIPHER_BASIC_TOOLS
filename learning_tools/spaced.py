from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from typing import List, Dict, Any
import json
import sys

# SM-2 algorithm implementation
# Reference: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2

EF_MIN = 1.3

@dataclass
class Card:
    id: str
    question: str
    answer: str
    interval_days: int = 0
    repetition: int = 0
    ease_factor: float = 2.5
    due: str = None  # ISO date string

    def review(self, quality: int, today: date | None = None) -> None:
        if today is None:
            today = date.today()
        if quality < 0 or quality > 5:
            raise ValueError("quality must be 0..5")

        if quality < 3:
            self.repetition = 0
            self.interval_days = 1
        else:
            if self.repetition == 0:
                self.interval_days = 1
            elif self.repetition == 1:
                self.interval_days = 6
            else:
                self.interval_days = int(round(self.interval_days * self.ease_factor))
            self.repetition += 1
            self.ease_factor = max(EF_MIN, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

        self.due = (today + timedelta(days=self.interval_days)).isoformat()

def load_deck(path: str) -> List[Card]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    cards: List[Card] = []
    for item in raw.get("cards", []):
        cards.append(Card(**item))
    return cards

def save_deck(path: str, cards: List[Card]) -> None:
    out = {"cards": [asdict(c) for c in cards]}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

def due_today(cards: List[Card], today: date | None = None) -> List[Card]:
    if today is None:
        today = date.today()
    result: List[Card] = []
    for c in cards:
        if c.due is None:
            result.append(c)
        else:
            try:
                due_date = date.fromisoformat(c.due)
                if due_date <= today:
                    result.append(c)
            except ValueError:
                result.append(c)  # invalid date -> treat as due
    return result

def cli_spaced(deck_path: str) -> int:
    cards = load_deck(deck_path)
    queue = due_today(cards)
    if not queue:
        print("No cards due today.")
        return 0
    print(f"{len(queue)} card(s) due. Enter quality 0-5 (or 'q' to quit).")
    id_to_card = {c.id: c for c in cards}
    for card in queue:
        print("- Question:", card.question)
        input("Press Enter to show answer...")
        print("  Answer:", card.answer)
        while True:
            q = input("Quality (0-5) > ").strip().lower()
            if q == 'q':
                save_deck(deck_path, cards)
                return 0
            if q in {'0','1','2','3','4','5'}:
                quality = int(q)
                break
            print("Please enter a number 0..5 or 'q'.")
        card.review(quality)
        id_to_card[card.id] = card
        print(f"  Next due: {card.due} | EF={card.ease_factor:.2f} | I={card.interval_days} | R={card.repetition}")
        print()
    save_deck(deck_path, cards)
    print("Session complete.")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m learning_tools.spaced <deck.json>")
        raise SystemExit(2)
    raise SystemExit(cli_spaced(sys.argv[1]))
