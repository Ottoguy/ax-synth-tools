"""Download Gordon Reid's "Synth Secrets" (Sound On Sound, 63 parts,
May 1999 - July 2004) as clean Markdown, one file per article.

  py -3 research/tools/fetch_synth_secrets.py [outdir]     (default reference/synth-secrets)

Source: https://www.soundonsound.com/series/synth-secrets-sound-sound
The articles are copyrighted by SOS Publications. The output folder is
git-ignored (like docs/); only our own derived notes (knowledge/) are tracked.

Output: NN-<slug>.md (NN = part number 01-63, in publication order) with a
metadata header, the intro, headings (##), paragraphs, list items, table rows
and figure captions as "[Figure: ...]". Images are not downloaded. Also writes
index.md and index.json. Polite: one request per ~1.5 s, reuses files that
already exist unless --force is given.
"""
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERIES = "https://www.soundonsound.com/series/synth-secrets-sound-sound"
UA = {"User-Agent": "Mozilla/5.0 (ax-synth-ai research; personal use)"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def index(page):
    items = []
    pat = (r'<article id="node-\d+"[^>]*about="(/techniques/[^"]+)".*?<h2 class="title"[^>]*><a[^>]*>(.*?)</a>'
           r'.*?field--subtitle">\s*(.*?)\s*</span>.*?field--body">\s*<p>(.*?)</p>.*?Published ([A-Za-z]+ \d{4})')
    for m in re.finditer(pat, page, re.S):
        if m.group(3).strip() != "Synth Secrets":
            continue
        items.append({"url": "https://www.soundonsound.com" + m.group(1), "slug": m.group(1).rsplit("/", 1)[1],
                      "title": html.unescape(m.group(2)).strip(),
                      "teaser": text(m.group(4)), "published": m.group(5)})
    return items   # the series page lists them in publication order


def text(fragment):
    fragment = re.sub(r"<br\s*/?>", " ", fragment)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def article_markdown(page):
    start = page.find('<div  class="node__content">')
    end = page.find('<div class="paging">', start)
    if start < 0 or end < 0:
        raise ValueError("article body markers not found")
    body = page[start:end]
    author = re.search(r'field--author">By <a[^>]*>(.*?)</a>', body)
    body = body[body.find("</div>", body.find("field--issue-date")) + 6:]   # skip the header group
    out = []
    # captions are nested inside <p>; pull them out first so the paragraph text stays clean
    body = re.sub(r'<span class="caption"[^>]*>(.*?)</span>', lambda m: f"\n@@CAPTION@@{text(m.group(1))}@@\n", body, flags=re.S)
    body = re.sub(r"<img[^>]*>", "", body)
    for m in re.finditer(r"<(h[1-6]|p|li|tr)\b[^>]*>(.*?)</\1>", body, re.S):
        tag, inner = m.group(1), m.group(2)
        caps = re.findall(r"@@CAPTION@@(.*?)@@", inner, re.S)
        inner = re.sub(r"@@CAPTION@@.*?@@", "", inner, flags=re.S)
        for c in caps:
            out.append(f"[Figure: {c.strip()}]")
        if tag == "tr":
            cells = [text(c) for c in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", inner, re.S)]
            if any(cells):
                out.append("| " + " | ".join(cells) + " |")
            continue
        t = text(inner)
        if not t:
            continue
        if tag.startswith("h"):
            out.append("## " + t)
        elif tag == "li":
            out.append("- " + t)
        else:
            out.append(t)
    return (author.group(1) if author else "Gordon Reid"), "\n\n".join(out)


def main(argv):
    force = "--force" in argv
    argv = [a for a in argv if a != "--force"]
    outdir = Path(argv[0]) if argv else ROOT / "reference" / "synth-secrets"
    outdir.mkdir(parents=True, exist_ok=True)
    items = index(get(SERIES))
    if len(items) != 63:
        print(f"WARNING: expected 63 articles, found {len(items)}")
    for n, it in enumerate(items, 1):
        it["part"] = n
        it["file"] = f"{n:02d}-{it['slug']}.md"
        dest = outdir / it["file"]
        if dest.exists() and not force:
            it["words"] = len(dest.read_text(encoding="utf-8").split())
            continue
        time.sleep(1.5)
        author, md = article_markdown(get(it["url"]))
        head = (f"# Synth Secrets, Part {n}: {it['title']}\n\n"
                f"- Author: {author}\n- Published: Sound On Sound, {it['published']}\n"
                f"- Source: {it['url']}\n- Copyright: SOS Publications Group. Local reference copy, not for redistribution.\n\n"
                f"> {it['teaser']}\n\n")
        dest.write_text(head + md + "\n", encoding="utf-8")
        it["words"] = len((head + md).split())
        print(f"{it['file']:60s} {it['words']:6d} words")
    (outdir / "index.json").write_text(json.dumps(items, indent=1, ensure_ascii=False), encoding="utf-8")
    lines = ["# Synth Secrets (Gordon Reid, Sound On Sound 1999-2004): local copies", "",
             f"Source: {SERIES}. Fetched by `research/tools/fetch_synth_secrets.py`. Copyrighted; git-ignored.", "",
             "| Part | Published | Title | File | Words |", "|---|---|---|---|---|"]
    lines += [f"| {i['part']} | {i['published']} | {i['title']} | `{i['file']}` | {i['words']} |" for i in items]
    (outdir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(items)} articles, {sum(i['words'] for i in items)} words -> {outdir}")


if __name__ == "__main__":
    main(sys.argv[1:])
