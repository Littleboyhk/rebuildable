"""Check 7: example settings plus simple secret-pattern scanning."""

from __future__ import annotations

import re
from pathlib import Path

from ..models import CheckResult, ScanContext
from .common import result, root_files

SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password|passwd|private[_-]?key)\s*[:=]\s*['\"]?(?!your[_-]|example|changeme|replace|<)[A-Za-z0-9+/=_-]{8,}"),
)


def run(context: ScanContext) -> CheckResult:
    files = root_files(context)
    example = files.get(".env.example")
    secret_hits: list[str] = []
    for source in context.files:
        if Path(source.path).name.lower() in {".env.example", ".env.sample", ".env.template"}:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(source.content):
                secret_hits.append(source.path)
                break
    if example is not None and not secret_hits:
        return result(7, "Settings and secrets", True, ".env.example exists and no common hardcoded secret patterns were found.", "No action needed.")
    reasons = []
    if example is None:
        reasons.append(".env.example is missing")
    if secret_hits:
        reasons.append("possible secrets in " + ", ".join(secret_hits[:3]))
    return result(7, "Settings and secrets", False, "; ".join(reasons) + ".", "Commit .env.example with blank placeholders and move credentials to environment variables.")
