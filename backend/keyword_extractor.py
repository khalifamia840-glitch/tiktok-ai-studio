"""
keyword_extractor.py
Extracts a list of exactly `count` keywords from a given topic string.
"""

import re


_DEFAULT_KEYWORDS = ["video", "content", "story"]


def extract_keywords(topic: str, count: int) -> list[str]:
    """
    Derive `count` keywords from `topic`.

    - Splits the topic into distinct words/phrases and deduplicates them.
    - If the topic is empty or whitespace-only, uses the default keywords
      ["video", "content", "story"].
    - If there are fewer distinct concepts than `count`, cycles/varies the
      existing keywords (appending an index suffix on repeated passes) to
      fill all slots.
    - Always returns a list of exactly `count` strings.

    Args:
        topic: A free-form text string describing the video topic.
        count: The exact number of keywords to return (must be >= 1).

    Returns:
        A list of exactly `count` keyword strings.
    """
    if count <= 0:
        return []

    # Normalise and split the topic into candidate keywords
    stripped = topic.strip() if topic else ""

    if not stripped:
        base_keywords = list(_DEFAULT_KEYWORDS)
    else:
        # Split on whitespace and common punctuation; keep non-empty tokens
        tokens = re.split(r"[\s,;.!?/|\\]+", stripped)
        tokens = [t.lower() for t in tokens if t]

        # Deduplicate while preserving order
        seen: set[str] = set()
        base_keywords: list[str] = []
        for token in tokens:
            if token not in seen:
                seen.add(token)
                base_keywords.append(token)

        # Fall back to defaults if splitting produced nothing useful
        if not base_keywords:
            base_keywords = list(_DEFAULT_KEYWORDS)

    # Fill up to `count` by cycling through base_keywords.
    # On the first pass (pass_index == 0) use the keyword as-is.
    # On subsequent passes append "_<pass_index>" to create variations.
    result: list[str] = []
    pass_index = 0
    while len(result) < count:
        for kw in base_keywords:
            if len(result) >= count:
                break
            if pass_index == 0:
                result.append(kw)
            else:
                result.append(f"{kw}_{pass_index}")
        pass_index += 1

    return result