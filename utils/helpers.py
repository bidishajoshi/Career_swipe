import re

def allowed_file(filename, allowed):
    """Check if a file extension is in the allowed set."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed

_LOCATION_ICON_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\u2600-\u27BF"
    "]+"
)


def _clean_location_part(value):
    value = _LOCATION_ICON_RE.sub("", str(value))
    value = re.sub(r"\s+", " ", value).strip(" \t\r\n-")
    value = re.sub(r"\bremote\b", "All Over", value, flags=re.IGNORECASE)
    return value


def format_job_location(loc_str):
    """
    Return a DB-backed job location with one pin, duplicate names removed, and
    Remote displayed as All Over.
    """
    if not loc_str:
        return "\U0001F4CD Location Not Specified"

    parts = [
        _clean_location_part(part)
        for part in re.split(r"[,;|]+", str(loc_str))
    ]

    unique = []
    seen = set()
    for part in parts:
        if not part:
            continue
        key = part.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(part)

    if not unique:
        return "\U0001F4CD Location Not Specified"

    return f"\U0001F4CD {', '.join(unique)}"
