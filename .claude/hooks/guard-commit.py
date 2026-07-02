#!/usr/bin/env python3
"""PreToolUse guard for Bash git commits.

Blocks commits whose message carries a Co-Authored-By trailer (repo convention:
no co-author attribution). Exit 2 + stderr blocks the call.
"""

import json
import re
import sys

CO_AUTHOR = re.compile(r"co-authored-by", re.IGNORECASE)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if "git commit" in command and CO_AUTHOR.search(command):
        print(
            "Blocked: this commit message contains a Co-Authored-By trailer. "
            "This repo omits co-author attribution - remove it and retry.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
