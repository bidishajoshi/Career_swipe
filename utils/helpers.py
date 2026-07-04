import re

def allowed_file(filename, allowed):
    """Check if a file extension is in the allowed set."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def format_job_location(loc_str) -> str:
    """
    Format job location string to display only once and remove duplicate icons.
    - If job location is 'Remote', returns '🌍 Remote'.
    - If empty or NULL, returns '📍 Location Not Specified'.
    - Otherwise, returns a cleaned string with single '📍' emoji and properly deduplicated locations.
    """
    if not loc_str:
        return "📍 Location Not Specified"
        
    cleaned = str(loc_str).strip()
    
    # Strip any existing 📍 or 🌍 or other emojis
    cleaned = re.sub(r'[\u2700-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDD00-\uDFFF]', '', cleaned)
    cleaned = cleaned.strip()
    
    if not cleaned:
        return "📍 Location Not Specified"
        
    # Split by comma or whitespace to find duplicates
    parts = [p.strip() for p in re.split(r'[,\s]+', cleaned) if p.strip()]
    unique_parts = []
    seen = set()
    for p in parts:
        p_lower = p.lower()
        if p_lower not in seen:
            seen.add(p_lower)
            # Standardize common terms
            if p_lower == 'nepal':
                unique_parts.append('Nepal')
            elif p_lower == 'singapore':
                unique_parts.append('Singapore')
            elif p_lower == 'india':
                unique_parts.append('India')
            elif p_lower == 'usa' or p_lower == 'us' or p_lower == 'united states':
                unique_parts.append('USA')
            else:
                # Capitalize first letter of arbitrary location names
                unique_parts.append(p[0].upper() + p[1:] if len(p) > 1 else p.upper())
                
    # Check if Remote
    if any(p.lower() == 'remote' for p in unique_parts):
        return "🌍 Remote"
        
    # Resolve single country or deduplicate country name
    if len(unique_parts) == 1:
        return f"📍 {unique_parts[0]}"
        
    # Deduplicate resolved country names
    final_parts = []
    seen_final = set()
    for p in unique_parts:
        p_lower = p.lower()
        if p_lower not in seen_final:
            seen_final.add(p_lower)
            final_parts.append(p)
            
    # If final parts consists only of a single country
    if len(final_parts) == 1:
        return f"📍 {final_parts[0]}"
        
    return f"📍 {', '.join(final_parts)}"

