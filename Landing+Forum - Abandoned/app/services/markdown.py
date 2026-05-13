import markdown

import bleach
from bleach.css_sanitizer import CSSSanitizer


ALLOWED_TAGS = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr",
    "strong", "em", "b", "i", "u", "s", "strike", "del",
    "blockquote", "q", "cite",
    "pre", "code", "kbd", "samp", "var",
    "ul", "ol", "li",
    "dl", "dt", "dd",
    "table", "thead", "tbody", "tfoot", "tr", "th", "td",
    "a", "img",
    "div", "span",
    "abbr", "acronym",
    "sup", "sub",
    "details", "summary",
]

ALLOWED_ATTRIBUTES = {
    "*": ["class", "id"],
    "a": ["href", "title", "rel", "target"],
    "img": ["src", "alt", "title", "width", "height"],
    "abbr": ["title"],
    "acronym": ["title"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan", "scope"],
    "code": ["class"],
    "pre": ["class"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto", "ftp"]

css_sanitizer = CSSSanitizer(
    allowed_css_properties=["color", "background-color", "text-align"]
)

MARKDOWN_EXTENSIONS = [
    "markdown.extensions.fenced_code",
    "markdown.extensions.codehilite",
    "markdown.extensions.tables",
    "markdown.extensions.toc",
    "markdown.extensions.nl2br",
    "markdown.extensions.sane_lists",
    "markdown.extensions.smarty",
]

MARKDOWN_EXTENSION_CONFIGS = {
    "markdown.extensions.codehilite": {
        "css_class": "highlight",
        "guess_lang": True,
        "use_pygments": False,
    },
    "markdown.extensions.toc": {
        "permalink": True,
        "permalink_class": "toc-link",
    },
}

md = markdown.Markdown(
    extensions=MARKDOWN_EXTENSIONS,
    extension_configs=MARKDOWN_EXTENSION_CONFIGS,
)


def render_markdown(content: str) -> str:
    if not content:
        return ""

    md.reset()

    html = md.convert(content)
    sanitized = sanitize_html(html)

    return sanitized


def sanitize_html(html: str) -> str:
    if not html:
        return ""

    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        css_sanitizer=css_sanitizer,
        strip=True,
    )

    clean_html = bleach.linkify(
        clean_html,
        callbacks=[_set_link_attributes],
        skip_tags=["pre", "code"],
        parse_email=False,
    )

    return clean_html


def _set_link_attributes(attrs, new=False):
    attrs[(None, "rel")] = "noopener noreferrer"
    attrs[(None, "target")] = "_blank"
    return attrs
