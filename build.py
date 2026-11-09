"""Builds the static pages GitHub Pages serves at youngestingabout.github.io/valiant.

Terms and Privacy come from src/, copies of valiant-content's legal/ texts (the same ones
the app bundles). Support is written here and is the one place the support email is shown.

    python3 build.py
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
SUPPORT_EMAIL = "eli@readojo.com"

# Where each language lives: English at the root, Spanish under es/.
PREFIX = {"en": "", "es": "es/"}

SUPPORT = {
    "en": {
        "title": "Support",
        "body": [
            ("p", f"Questions about Valiant? Write to [{SUPPORT_EMAIL}](mailto:{SUPPORT_EMAIL})."),
            ("h", "Your subscription"),
            ("p", "Manage or cancel it in your App Store account settings. Apple handles payments and refunds."),
            ("h", "Delete your account"),
            ("p", "In Valiant, go to You, then Delete my account and data."),
            ("p", "[Privacy Policy]({up}privacy/) · [Terms of Use]({up}terms/)"),
        ],
    },
    "es": {
        "title": "Ayuda",
        "body": [
            ("p", f"¿Preguntas sobre Valiant? Escribe a [{SUPPORT_EMAIL}](mailto:{SUPPORT_EMAIL})."),
            ("h", "Tu suscripción"),
            ("p", "Adminístrala o cancélala en los ajustes de tu cuenta del App Store. Apple gestiona los pagos y reembolsos."),
            ("h", "Borrar tu cuenta"),
            ("p", "En Valiant, ve a Tú, luego Borrar mi cuenta y mis datos."),
            ("p", "[Política de privacidad]({up}privacy/) · [Condiciones de uso]({up}terms/)"),
        ],
    },
}

INDEX = {
    "en": ("Valiant", "Bible for Men.", [("Support", "support/"), ("Privacy Policy", "privacy/"), ("Terms of Use", "terms/"), ("Español", "es/")]),
    "es": ("Valiant", "Biblia para hombres.", [("Ayuda", "support/"), ("Política de privacidad", "privacy/"), ("Condiciones de uso", "terms/"), ("English", "../")]),
}

STYLE = """
:root { color-scheme: light; }
body { margin: 0; background: #FFF6DC; color: #113A4E;
  font: 17px/1.6 -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; }
main { max-width: 680px; margin: 0 auto; padding: 40px 20px 64px; }
h1, h2 { font-family: Georgia, "Times New Roman", serif; line-height: 1.15; }
h1 { font-size: 40px; margin: 0 0 6px; }
h2 { font-size: 24px; margin: 32px 0 8px; }
.updated { color: #2C5163; font-size: 15px; margin: 0 0 20px; }
p, li { margin: 0 0 10px; }
ul { padding-left: 20px; }
a { color: #1A6D8E; }
.brand { color: #1A6D8E; font-weight: 600; letter-spacing: .02em; margin: 0 0 28px; text-decoration: none; display: inline-block; }
"""


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', out)


def render_markdown(text: str) -> tuple[str, str]:
    """# title, the Updated line, ## headings, paragraphs and - items."""
    title, parts, items = "", [], []

    def flush() -> None:
        if items:
            parts.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
            items.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush()
        elif line.startswith("# "):
            title = line[2:]
        elif line.startswith("## "):
            flush()
            parts.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("- "):
            items.append(inline(line[2:]))
        elif title and not parts:
            parts.append(f'<p class="updated">{inline(line)}</p>')
        else:
            flush()
            parts.append(f"<p>{inline(line)}</p>")
    flush()
    return title, "\n".join(parts)


def page(lang: str, title: str, body: str, home: str) -> str:
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · Valiant</title><style>{STYLE}</style></head>
<body><main><a class="brand" href="{home}">Valiant</a><h1>{html.escape(title)}</h1>
{body}
</main></body></html>
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build() -> None:
    for lang, prefix in PREFIX.items():
        base = ROOT / prefix
        for name in ("privacy", "terms"):
            title, body = render_markdown((SRC / f"{name}.{lang}.md").read_text(encoding="utf-8"))
            write(base / name / "index.html", page(lang, title, body, "../"))
        copy = SUPPORT[lang]
        body = "\n".join(
            f"<h2>{inline(t)}</h2>" if kind == "h" else f"<p>{inline(t.format(up='../'))}</p>"
            for kind, t in copy["body"]
        )
        write(base / "support" / "index.html", page(lang, copy["title"], body, "../"))
        name, line, links = INDEX[lang]
        body = f"<p>{html.escape(line)}</p>\n<ul>" + "".join(f'<li><a href="{h}">{html.escape(t)}</a></li>' for t, h in links) + "</ul>"
        write(base / "index.html", page(lang, name, body, "./"))


if __name__ == "__main__":
    build()
