#!/usr/bin/env python3
"""PostToolUse auto-formatter for Edit/Write/MultiEdit.

Formats the edited file in place: ruff for Python (via uvx), the project's
local eslint --fix for TS/JS. Never blocks - missing tools are skipped silently.
"""

import json
import os
import shutil
import subprocess
import sys


def run(cmd, cwd=None):
    try:
        subprocess.run(
            cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=30, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        pass


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    file_path = (
        data.get("tool_response", {}).get("filePath")
        or data.get("tool_input", {}).get("file_path")
    )
    if not file_path or not os.path.isfile(file_path):
        sys.exit(0)

    project = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

    if file_path.endswith(".py"):
        if shutil.which("ruff"):
            run(["ruff", "format", file_path])
        elif shutil.which("uvx"):
            run(["uvx", "ruff", "format", file_path])

    elif file_path.endswith((".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")):
        frontend = os.path.join(project, "frontend")
        eslint = os.path.join(frontend, "node_modules", ".bin", "eslint")
        if os.path.isfile(eslint):
            run([eslint, "--fix", file_path], cwd=frontend)

    sys.exit(0)


if __name__ == "__main__":
    main()
