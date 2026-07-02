#!/usr/bin/env python3
"""PreToolUse guard for Edit/Write/MultiEdit.

Blocks writes that violate two AGENTS.md non-negotiables:
  - companyTaxId is never logged; secrets are never hardcoded.
  - TypeScript is strict - no `any`.

Exit 2 + stderr blocks the tool call and feeds the reason back to the model.
"""

import json
import re
import sys


def content_to_check(tool_name, tool_input):
    if tool_name == "Write":
        return tool_input.get("content", "")
    if tool_name == "Edit":
        return tool_input.get("new_string", "")
    if tool_name == "MultiEdit":
        return "\n".join(e.get("new_string", "") for e in tool_input.get("edits", []))
    return ""


LOG_SINK = re.compile(
    r"\b(print|console\.(log|error|warn|info|debug)|logger|logging"
    r"|\.(info|debug|warning|warn|error|exception|critical))\b",
    re.IGNORECASE,
)
TAX_ID = re.compile(r"company_?tax_?id", re.IGNORECASE)
JWT = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")
HARDCODED_KEY = re.compile(r"SUPABASE_SERVICE_KEY\s*[:=]\s*[\"'][^\"']", re.IGNORECASE)

ANY_PATTERNS = [
    re.compile(r":\s*any\b"),
    re.compile(r"\bas\s+any\b"),
    re.compile(r"<\s*any\s*>"),
    re.compile(r"\bany\[\]"),
    re.compile(r"Array<\s*any\s*>"),
    re.compile(r"Record<[^>]*\bany\b[^>]*>"),
]

# `overdue` is derived (is_overdue), never a stored status. These match only
# attempts to make it a status value - not the legitimate `overdue: bool` field.
OVERDUE_STATUS = [
    re.compile(r"OVERDUE\s*=\s*[\"']overdue[\"']"),
    re.compile(r"\bStatus\.OVERDUE\b"),
    re.compile(r"status\s*[:=]\s*[\"']overdue[\"']", re.IGNORECASE),
    re.compile(r"Literal\[[^\]]*[\"']overdue[\"']"),
]


def find_violations(file_path, content):
    violations = []
    is_ts = file_path.endswith((".ts", ".tsx")) and not file_path.endswith(".d.ts")

    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.lstrip()

        if TAX_ID.search(line) and LOG_SINK.search(line) and "mask" not in line.lower():
            violations.append(
                f"  line {i}: companyTaxId flows into a log/print sink - "
                f"it must never be logged.\n    {stripped[:120]}"
            )

        if JWT.search(line) or HARDCODED_KEY.search(line):
            violations.append(
                f"  line {i}: looks like a hardcoded secret / service key - "
                f"read it from the environment instead.\n    {stripped[:80]}"
            )

        if is_ts and not stripped.startswith(("//", "*", "/*")):
            if any(p.search(line) for p in ANY_PATTERNS):
                violations.append(
                    f"  line {i}: `any` is banned (TypeScript strict).\n    {stripped[:120]}"
                )

        if any(p.search(line) for p in OVERDUE_STATUS):
            violations.append(
                f"  line {i}: `overdue` must be derived (is_overdue), never a stored "
                f"status.\n    {stripped[:120]}"
            )

    return violations


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = content_to_check(data.get("tool_name", ""), tool_input)
    if not content:
        sys.exit(0)

    violations = find_violations(file_path, content)
    if violations:
        print(
            "Blocked by domain guard (AGENTS.md non-negotiables):\n"
            + "\n".join(violations),
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
