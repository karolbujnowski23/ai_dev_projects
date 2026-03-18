# -*- coding: utf-8 -*-

#   logger.py

import sys

class Logger:
    @staticmethod
    def box(text: str) -> None:
        lines = text.split("\n")
        width = max(len(l) for l in lines) + 4
        print("\n" + "╔" + "═" * (width - 2) + "╗")
        for line in lines:
            print(f"║ {line:<{width-4}} ║")
        print("╚" + "═" * (width - 2) + "╝\n")

    @staticmethod
    def start(text: str) -> None:
        print(f"⏳ {text}", end="\r")

    @staticmethod
    def success(text: str) -> None:
        print(f"✅ {text}")

    @staticmethod
    def error(text: str) -> None:
        print(f"❌ {text}", file=sys.stderr)

    @staticmethod
    def info(text: str) -> None:
        print(f"ℹ️ {text}")

log = Logger()
