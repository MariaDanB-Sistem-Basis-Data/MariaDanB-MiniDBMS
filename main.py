from __future__ import annotations
import sys
from cli import run

def main(argv: list[str] | None = None) -> None:
    run(sys.argv[1:] if argv is None else argv)

main()