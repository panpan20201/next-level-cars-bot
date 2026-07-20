import re

def format_number(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", " ")

def parse_smart_number(text: str) -> float | None:
    if not text: return None
    clean = text.strip().lower().replace(" ", "").replace(",", ".")
    pattern = re.compile(r'([0-9.]+)\s*([а-яa-z]*)')
    matches = pattern.findall(clean)
    if not matches: return None
    total_sum = 0.0
    for val_str, suffix in matches:
        try:
            val = float(val_str)
            if suffix in ["млн", "м", "m"]: val *= 1_000_000
            elif suffix in ["млрд"]: val *= 1_000_000_000
            elif suffix in ["к", "k", "тыс"]: val *= 1_000
            total_sum += val
        except ValueError: continue
    return total_sum