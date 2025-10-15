from __future__ import annotations
from datetime import date
from typing import Literal

TEMPLATE_TYPES = ("zettelkasten", "cornell", "project")


def generate_template(template_type: str, title: str) -> str:
    today = date.today().isoformat()
    if template_type == "zettelkasten":
        return f"""---
created: {today}
updated: {today}
tags: []
---

# {title}

## Summary

## Notes

## Links
"""
    if template_type == "cornell":
        return f"""# {title}

## Cues
- 

## Notes
- 

## Summary

"""
    if template_type == "project":
        return f"""# {title}

## Goals
- 

## Tasks
- [ ] 

## Decisions
- 

## Notes
- 
"""
    raise ValueError("Unknown template type. Use one of: " + ", ".join(TEMPLATE_TYPES))


def write_template(output_path: str, template_type: str, title: str) -> int:
    content = generate_template(template_type, title)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote {template_type} template to {output_path}")
    return 0
