import re
from datetime import datetime


def count_words(text: str) -> int:
    """Count words in text, excluding hashtags."""
    lines = text.split('\n')
    word_lines = [l for l in lines if not l.strip().startswith('#')]
    clean = ' '.join(word_lines)
    words = clean.split()
    return len(words)


def count_emojis(text: str) -> int:
    """Count emoji characters in text."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F9FF"
        "\U00002700-\U000027BF"
        "\U0001FA00-\U0001FA6F"
        "]+",
        flags=re.UNICODE
    )
    return len(emoji_pattern.findall(text))


def format_word_count_badge(count: int) -> tuple[str, str]:
    """Return (label, color) for word count badge."""
    if count <= 180:
        return f"✅ {count} words", "green"
    elif count <= 220:
        return f"⚠️ {count} words", "orange"
    else:
        return f"❌ {count} words (over limit)", "red"


def extract_sections(post: str) -> dict:
    """Attempt to extract post sections for display."""
    lines = [l for l in post.split('\n') if l.strip()]
    sections = {
        "hook": "",
        "description": "",
        "highlights": [],
        "closing": "",
        "hashtags": []
    }
    
    hashtag_lines = []
    content_lines = []
    
    for line in lines:
        if line.strip().startswith('#') and len(line.strip().split()[0]) > 1:
            hashtag_lines.append(line.strip())
        else:
            content_lines.append(line.strip())
    
    sections["hashtags"] = hashtag_lines
    
    bullets = []
    non_bullets = []
    
    for line in content_lines:
        if line.startswith('•') or line.startswith('-') or line.startswith('*'):
            bullets.append(line)
        else:
            non_bullets.append(line)
    
    sections["highlights"] = bullets
    
    if non_bullets:
        sections["hook"] = non_bullets[0]
    if len(non_bullets) >= 3:
        sections["description"] = '\n'.join(non_bullets[1:-1])
        sections["closing"] = non_bullets[-1]
    elif len(non_bullets) == 2:
        sections["description"] = non_bullets[1]
    
    return sections


def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
