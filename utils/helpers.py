import re

def allowed_file(filename, allowed):
    """Check if a file extension is in the allowed set."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed

def format_job_location(loc_str):
    """
    Format job location string to display only once and remove duplicate icons.
    - If job location is 'Remote' alone, returns '🌍 Remote (Worldwide)'.
    - If job location includes 'Remote' with other locations, returns locations with a trailing '🌍 All Over'.
    - If empty or NULL, returns '📍 Location Not Specified'.
    - Otherwise, returns a cleaned string with a single '📍' emoji and deduplicated locations.
    """
    if not loc_str:
        return "📍 Location Not Specified"

    # Split by commas, pipes or semicolons and strip whitespace
    parts = [p.strip() for p in re.split(r"[,:;|]+", str(loc_str)) if p.strip()]
    cleaned_parts = []
    for p in parts:
        # Remove any emoji or special characters
        p_clean = re.sub(r"[\u2700-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDD00-\uDFFF]", "", p)
        p_clean = p_clean.strip()
        if not p_clean:
            continue
        if p_clean.lower() == "remote":
            cleaned_parts.append("remote")
        else:
            # Capitalize each word (e.g., united states -> United States)
            cleaned_parts.append(" ".join(word.capitalize() for word in p_clean.split()))

    # Deduplicate case‑insensitively while preserving order
    unique = []
    seen = set()
    for p in cleaned_parts:
        low = p.lower()
        if low not in seen:
            seen.add(low)
            unique.append(p)

    remote_present = any(p.lower() == "remote" for p in unique)
    other = [p for p in unique if p.lower() != "remote"]

    if remote_present:
        if other:
            return f"📍 {', '.join(other)} 🌍 All Over"
        else:
            return "🌍 Remote (Worldwide)"

    if len(other) == 1:
        return f"📍 {other[0]}"
    return f"📍 {', '.join(other)}"
