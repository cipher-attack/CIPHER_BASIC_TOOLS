#!/usr/bin/env python3
import argparse
import sys
from .spaced import cli_spaced
from .recall import generate_from_markdown
from .notes import write_template, TEMPLATE_TYPES
from .pomodoro import run_pomodoro

def main(argv=None):
    parser = argparse.ArgumentParser(prog="learning-tools", description="Learning tools CLI suite")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # spaced repetition placeholder
    sp = subparsers.add_parser("spaced", help="Spaced repetition scheduler")
    sp.add_argument("--deck", required=True, help="Path to JSON deck file")
    sp.set_defaults(func=lambda args: cli_spaced(args.deck))

    # active recall placeholder
    ar = subparsers.add_parser("recall", help="Generate active recall prompts from markdown")
    ar.add_argument("--input", required=True, help="Markdown file or directory")
    ar.add_argument("--out", required=True, help="Output JSON deck file")
    ar.set_defaults(func=lambda args: generate_from_markdown(args.input, args.out))

    # note templates placeholder
    nt = subparsers.add_parser("notes", help="Generate note templates")
    nt.add_argument("--out", required=True, help="Output path for template")
    nt.add_argument("--type", required=True, choices=list(TEMPLATE_TYPES), help="Template type")
    nt.add_argument("--title", required=True, help="Template title")
    nt.set_defaults(func=lambda args: write_template(args.out, args.type, args.title))

    # pomodoro placeholder
    pomo = subparsers.add_parser("pomo", help="Pomodoro timer")
    pomo.add_argument("--work", type=int, default=25, help="Work minutes")
    pomo.add_argument("--short", type=int, default=5, help="Short break minutes")
    pomo.add_argument("--long", type=int, default=15, help="Long break minutes")
    pomo.add_argument("--cycles", type=int, default=4, help="Number of work cycles before long break")
    pomo.set_defaults(func=lambda args: run_pomodoro(args.work, args.short, args.long, args.cycles))

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
