import re

INJECTION_PATTERNS = [
    re.compile(r"(ignore|disregard)\s+(all\s+)?(previous|prior)\s+(instructions|directives)", re.IGNORECASE),
    re.compile(r"system\s+(prompt|override)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(a|an)?", re.IGNORECASE),
    re.compile(r"override\s+system\s+directive", re.IGNORECASE),
    re.compile(r"bypass\s+safety\s+filter", re.IGNORECASE),
    re.compile(r"[A-Za-z0-9+/=]{500,}"),  # Suspicious long base64 blob
]



def detect_prompt_injection(text: str) -> tuple[bool, list[str]]:
    """Analyzes spatial text for prompt-injection markers."""
    detected: list[str] = []
    for pat in INJECTION_PATTERNS:
        match = pat.search(text)
        if match:
            snippet = match.group(0)[:40]
            detected.append(f"Suspicious pattern: '{snippet}'")

    return (len(detected) > 0, detected)


def scan_for_prompt_injection(text: str) -> tuple[bool, str | None]:
    has_injection, patterns = detect_prompt_injection(text)
    return (has_injection, patterns[0] if patterns else None)

