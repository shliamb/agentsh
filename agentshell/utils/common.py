


def t(text, lang: str, key: str, **kw) -> str:
    table = text.get(lang) or text["en"]
    if key not in table:
        return f"[missing:{key}]"
    return table[key].format(**kw)