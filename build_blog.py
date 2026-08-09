#!/usr/bin/env python3
"""Сборка блога zerek.cc.

Читает разборы из _blog/*.md (frontmatter + markdown),
генерит:
  blog/index.html            — список разборов
  blog/<slug>/index.html     — страница разбора
  sitemap.xml                — карта сайта со всеми страницами

Запуск: python3 build_blog.py
"""

import html
import re
import shutil
from datetime import date
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).parent
SRC = ROOT / "_blog"
OUT = ROOT / "blog"
SITE = "https://zerek.cc"

# страны: код -> (флаг, подпись, порядок)
REGIONS = {
    "kz": ("🇰🇿", "Казахстан"),
    "ru": ("🇷🇺", "Россия"),
    "us": ("🇺🇸", "США"),
    "uz": ("🇺🇿", "Узбекистан"),
}

ARROW = '<svg viewBox="0 0 16 16"><path d="M4 12 12 4M6 4h6v6"/></svg>'
BACK_ARROW = '<svg viewBox="0 0 16 16"><path d="M12 4 4 12M10 12H4V6"/></svg>'

TG_ICON = ('<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 '
           '1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 '
           '2.71-2.48 2.76-2.69a.2.2 0 0 0-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.35-.01-1.02-.2-1.51-.37-.6-.2-1.08-.31-1.04-.66.02-.18.27-.36.75-.55 '
           '2.95-1.28 4.91-2.13 5.88-2.54 2.8-1.18 3.38-1.39 3.76-1.4.08 0 .27.02.39.12a.4.4 0 0 1 .12.27c0 .04-.01.12-.02.16z"/></svg>')
MAIL_ICON = '<svg viewBox="0 0 24 24"><path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4.2-8 5-8-5V6l8 5 8-5v2.2z"/></svg>'

SUN = ('<svg viewBox="0 0 24 24" class="theme-toggle-icon-sun" fill="none" stroke="currentColor" stroke-width="1.8" '
       'stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/>'
       '<line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>'
       '<line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/>'
       '<line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>'
       '<line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>')
MOON = ('<svg viewBox="0 0 24 24" class="theme-toggle-icon-moon" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" style="display:none;"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>')

MENU_ITEMS = [
    ("/#/research", "Аналитика рынка"),
    ("/#/services", "Финмодели"),
    ("/#/bizplans", "Бизнес-планы"),
    ("/#/accounting", "Управленческий учет"),
    ("/#/dashboards", "Дашборды"),
    (None, None),  # разделитель
    ("/blog/", "Блог"),
    ("/#/about", "Обо мне"),
    ("/#/contacts", "Контакты"),
]


def nav_links(sep_style):
    out = []
    for href, label in MENU_ITEMS:
        if href is None:
            out.append(f'    <div style="{sep_style}"></div>')
            continue
        cls = ' class="is-active"' if href == "/blog/" else ""
        out.append(f'    <a href="{href}"{cls}>{label}</a>')
    return "\n".join(out)


def chrome():
    """Сайдбар, мобильная шапка и мобильное меню — те же, что на главной."""
    photos = (
        '      <img src="/photo-light.webp" class="photo-light-img" alt="Финансист" width="256" height="256" decoding="async">\n'
        '      <img src="/photo-dark.webp" class="photo-dark-img" alt="Финансист" width="256" height="256" decoding="async" style="display:none;">'
    )
    sidebar_sep = "margin: 12px 14px 10px; border-top: 1px solid var(--line); opacity: 0.85;"
    veil_sep = "margin: 16px auto; border-top: 1px solid rgba(240,235,223,.15); width: 60px;"
    return f"""<div class="grain" aria-hidden="true"></div>

<aside class="sidebar">
  <a href="/" aria-label="Главная">
    <span class="sb__mark">
{photos}
    </span>
  </a>
  <div class="sb__name">ФИНАНСИСТ</div>
  <nav class="menu" data-menu id="sbMenu">
    <span class="menu__bubble" id="menuBubble" aria-hidden="true"></span>
{nav_links(sidebar_sep)}
  </nav>
  <div class="sb__foot">
    <a href="https://t.me/godoffin" aria-label="Telegram">{TG_ICON}</a>
    <a href="mailto:small.economy.kaz@gmail.com" aria-label="Почта">{MAIL_ICON}</a>
    <button id="themeToggle" class="theme-toggle-btn" aria-label="Сменить тему">
       {SUN}
       {MOON}
    </button>
  </div>
</aside>

<header class="mhead">
  <a class="mhead__brand" href="/">
    <span class="mhead__mark">
{photos}
    </span>
    <span>ФИНАНСИСТ</span>
  </a>
  <div style="display:flex;align-items:center;gap:12px;">
    <button id="themeToggleMob" class="theme-toggle-btn-mob" aria-label="Сменить тему">
       {SUN}
       {MOON}
    </button>
    <button class="burger" id="burger" aria-label="Меню"><span></span><span></span></button>
  </div>
</header>

<div class="veil" id="veil">
  <nav data-menu>
{nav_links(veil_sep)}
  </nav>
</div>"""


FOOTER = """<footer class="footer">
  <div class="wrap">
    <div style="text-transform:uppercase; letter-spacing:0.04em;">© 2026 ФИНАНСИСТ</div>
    <div>zerek.cc · <a href="/offer.html" target="_blank" style="text-decoration:underline; text-underline-offset:3px;">Публичная оферта</a></div>
    <div class="disc">Работаю с бизнесом из <span class="flag">🇷🇺</span> и <span class="flag">🇰🇿</span> от самозанятого.</div>
  </div>
</footer>"""

METRIKA = """<script type="text/javascript">
(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
m[i].l=1*new Date();
for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
(window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");
ym(111172932, "init", {clickmap:true, trackLinks:true, accurateTrackBounce:true, webvisor:true, trackHash:true});
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/111172932" style="position:absolute; left:-9999px;" alt=""></div></noscript>"""

FAVICON = ("<link rel=\"icon\" href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
           "<rect width='32' height='32' rx='9' fill='%231A1712'/><text x='16' y='23' font-size='19' "
           "font-family='Georgia,serif' font-weight='600' fill='%23F5F2EA' text-anchor='middle'>Ф</text></svg>\">")

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500'
         '&family=Manrope:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">')


def shell(title, description, canonical, body, jsonld="", og_type="article"):
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Финансист">
<meta property="og:locale" content="ru_RU">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{jsonld}
<meta name="theme-color" content="#F5F2EA">
{FAVICON}
{FONTS}
<link rel="stylesheet" href="/assets/site.css?v=15">
</head>
<body>

{chrome()}

<div class="content">
<main>
{body}
</main>

{FOOTER}
</div>

{METRIKA}
<script src="/assets/typo.js?v=2"></script>
<script src="/assets/blog.js?v=2"></script>
</body>
</html>
"""


CALC_RE = re.compile(r"<p>\[calc:(.+?)\]</p>\s*(<table>.*?</table>)(?:\s*<p>\[note:(.+?)\]</p>)?", re.S)

NBSP = " "
# разряды числа: 19 000 000 не должно разрываться переносом строки
_DIGIT_GROUP = re.compile(r"(?<=\d) (?=\d{3}(?!\d))")
# число и его единица: 175 тыс, 12%, 7,2 млн рублей
_UNIT = re.compile(r"(\d)\s+(₸|₽|%|млн|млрд|тыс|тысяч|миллион\w*|миллиард\w*|рубл\w+|тенге|процент\w*|квадратн\w+|кв\.м)")


def typo(text):
    """Русская типографика: числа и единицы не разрываются переносом."""
    text = _DIGIT_GROUP.sub(NBSP, text)
    text = _DIGIT_GROUP.sub(NBSP, text)  # второй проход для 19 000 000
    text = _UNIT.sub(r"\1" + NBSP + r"\2", text)
    return text


def render_body(md_text):
    """markdown -> html + оформление счётных блоков.

    Таблица, перед которой стоит [calc: подпись], оборачивается в .calc.
    Идущий следом [note: текст] становится сноской внутри блока.
    """
    body = markdown.markdown(typo(md_text), extensions=["tables", "attr_list"])

    def wrap(m):
        cap, table, note = m.group(1).strip(), m.group(2), m.group(3)
        note_html = f'<div class="calc__note">{note.strip()}</div>' if note else ""
        return (f'<div class="calc rv"><div class="calc__cap">{cap}</div>{table}{note_html}</div>')

    return CALC_RE.sub(wrap, body)


def load_posts():
    posts = []
    for path in sorted(SRC.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            raise SystemExit(f"{path.name}: нет frontmatter")
        _, fm, md_text = raw.split("---", 2)
        meta = yaml.safe_load(fm)
        meta["md"] = md_text.strip()
        meta["path"] = path
        for field in ("slug", "title", "niche", "region", "summary", "source"):
            if not meta.get(field):
                raise SystemExit(f"{path.name}: нет поля {field}")
        if meta["region"] not in REGIONS:
            raise SystemExit(f"{path.name}: неизвестная страна {meta['region']}")
        posts.append(meta)
    posts.sort(key=lambda p: p.get("order", 999))
    return posts


def post_page(post, prev_post, next_post):
    flag, region_name = REGIONS[post["region"]]
    url = f"{SITE}/blog/{post['slug']}/"

    facts = [f'<span class="article__fact">{html.escape(post["niche"])}</span>',
             f'<span class="article__fact">{flag} {region_name}</span>']
    if post.get("loss"):
        facts.append(f'<span class="article__fact article__fact--loss">{html.escape(post["loss"])}</span>')

    jsonld = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": {yaml.dump(post['title'], allow_unicode=True, default_flow_style=True).strip().rstrip('.')},
  "description": {yaml.dump(post['summary'], allow_unicode=True, default_flow_style=True).strip().rstrip('.')},
  "inLanguage": "ru",
  "mainEntityOfPage": "{url}",
  "image": "{SITE}/og.png",
  "author": {{"@type": "Organization", "name": "Финансист", "url": "{SITE}/"}},
  "publisher": {{"@type": "Organization", "name": "Финансист", "url": "{SITE}/"}}
}}
</script>"""

    nav = ""
    if prev_post or next_post:
        cells = []
        if prev_post:
            cells.append(f'<a href="/blog/{prev_post["slug"]}/"><span>Предыдущий разбор</span>'
                         f'<strong>{html.escape(prev_post["title"])}</strong></a>')
        else:
            cells.append("<div></div>")
        if next_post:
            cells.append(f'<a href="/blog/{next_post["slug"]}/"><span>Следующий разбор</span>'
                         f'<strong>{html.escape(next_post["title"])}</strong></a>')
        else:
            cells.append("<div></div>")
        nav = f'<div class="nextprev">{"".join(cells)}</div>'

    src_note = (f'<div class="article__src">{post["source_note"]}</div>'
                if post.get("source_note") else "")

    body = f"""<div class="progress" aria-hidden="true"><div class="progress__bar"></div></div>

<article class="page is-current">
  <div class="wrap sec sec--first hero-tight">
    <div class="article">
      <a class="article__crumb" href="/blog/">{BACK_ARROW} Все разборы</a>
      <h1>{html.escape(post["title"])}</h1>
      <div class="article__facts">{"".join(facts)}</div>
    </div>
  </div>

  <div class="wrap sec">
    <div class="article">
      <div class="article__body">
{render_body(post["md"])}
      </div>
      {src_note}
    </div>
  </div>

  <div class="wrap sec">
    <div class="dark-band rv">
      <span class="eyebrow">Ваша ниша</span>
      <p class="quote" style="margin-top:24px">Такой расчет можно сделать до того, как деньги вложены</p>
      <p class="sub">Финансовая модель показывает точку безубыточности, кассовый разрыв и запас прочности вашего проекта. Дешевле одной ошибки в аренде.</p>
      <div class="actions">
        <a class="btn" href="/#/services"><span>Про финмодели</span><span class="btn__ic">{ARROW}</span></a>
        <a class="btn btn--ghost" href="/#/contacts"><span>Обсудить задачу</span><span class="btn__ic">{ARROW}</span></a>
      </div>
    </div>
  </div>

  <div class="wrap sec sec--last">
    {nav}
  </div>
</article>"""

    title = f'{post["title"]} · Разбор'
    return shell(title, post["summary"], url, body, jsonld)


def index_page(posts):
    cards = []
    for i, p in enumerate(posts, 1):
        flag, region_name = REGIONS[p["region"]]
        loss = f'<span class="post__num">{html.escape(p["loss"])}</span>' if p.get("loss") else "<span></span>"
        cards.append(f"""      <a class="post rv" href="/blog/{p['slug']}/" data-region="{p['region']}">
        <span class="post__meta">{flag} {html.escape(p['niche'])}</span>
        <h2 class="post__title">{html.escape(p['title'])}</h2>
        <p class="post__sum">{html.escape(p['summary'])}</p>
        <span class="post__foot">
          {loss}
          <span class="post__go">Разбор {ARROW}</span>
        </span>
      </a>""")

    used = []
    for code in REGIONS:
        if any(p["region"] == code for p in posts):
            used.append(code)
    filters = ['<button class="filter is-on" data-filter="all">Все</button>']
    for code in used:
        flag, name = REGIONS[code]
        filters.append(f'<button class="filter" data-filter="{code}">{flag} {name}</button>')

    jsonld = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Blog",
  "name": "Блог Финансиста",
  "description": "Разборы экономики малого бизнеса: где именно проект теряет деньги и что показала бы финансовая модель до вложений",
  "url": "{SITE}/blog/",
  "inLanguage": "ru"
}}
</script>"""

    body = f"""<div class="page is-current">
  <div class="wrap sec sec--first hero-tight">
    <span class="eyebrow">База знаний</span>
    <h1 style="margin-top:26px">Разборы: где бизнес теряет деньги</h1>
    <p class="lead" style="margin-top:24px">Каждый разбор устроен одинаково: что произошло, где именно сломалась экономика и какие цифры показали бы это заранее. Реальные истории, живые суммы, никаких выдуманных ориентиров.</p>
  </div>

  <div class="wrap sec sec--last">
    <div class="filters">{"".join(filters)}</div>
    <div class="posts">
{chr(10).join(cards)}
    </div>
  </div>
</div>"""

    return shell(
        "Разборы: где бизнес теряет деньги · Финансист",
        "Разборы экономики малого бизнеса из Казахстана, России и США: что произошло, где сломалась экономика и что показала бы финансовая модель до вложений.",
        f"{SITE}/blog/",
        body,
        jsonld,
        og_type="website",
    )


def write_sitemap(posts):
    today = date.today().isoformat()
    urls = [(f"{SITE}/", "1.0", "weekly"), (f"{SITE}/blog/", "0.9", "weekly")]
    urls += [(f"{SITE}/blog/{p['slug']}/", "0.7", "monthly") for p in posts]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, prio, freq in urls:
        lines += ["  <url>", f"    <loc>{loc}</loc>", f"    <lastmod>{today}</lastmod>",
                  f"    <changefreq>{freq}</changefreq>", f"    <priority>{prio}</priority>", "  </url>"]
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    posts = load_posts()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    for i, p in enumerate(posts):
        prev_post = posts[i - 1] if i > 0 else None
        next_post = posts[i + 1] if i < len(posts) - 1 else None
        d = OUT / p["slug"]
        d.mkdir(parents=True)
        (d / "index.html").write_text(post_page(p, prev_post, next_post), encoding="utf-8")

    (OUT / "index.html").write_text(index_page(posts), encoding="utf-8")
    write_sitemap(posts)
    print(f"собрано разборов: {len(posts)}")
    for p in posts:
        print(f"  /blog/{p['slug']}/")


if __name__ == "__main__":
    main()
