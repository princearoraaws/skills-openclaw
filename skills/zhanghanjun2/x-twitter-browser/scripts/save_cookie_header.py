#!/usr/bin/env python3
from __future__ import annotations

import argparse

from session_lib import (
    load_cookie_header,
    resolve_runtime_dir,
    write_cookie_header,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Save an X cookie header into the skill runtime directory")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--cookie-header", help="Raw Cookie header string")
    source.add_argument("--cookie-file", help="File containing the raw Cookie header string")
    parser.add_argument("--runtime-dir", help="Override runtime directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runtime_dir = resolve_runtime_dir(args.runtime_dir)
    cookie_header = load_cookie_header(args.cookie_header, args.cookie_file, runtime_dir)
    cookie_path = write_cookie_header(runtime_dir, cookie_header)
    print(f"Saved cookie header to {cookie_path}")


if __name__ == "__main__":
    main()
