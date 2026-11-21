import html


def decode_html_text(text: str) -> str:
    return html.unescape(text).strip()
