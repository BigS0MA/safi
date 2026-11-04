#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""صافي — builds the library site from items/.

  python3 build.py            → site/index.html, site/p/<n>/index.html, site/_redirects

Each item lives in items/<NN>-<slug>/ with:
  item.json   n, slug, kind (prompt · trick · skill), title, hook, works_with, how[], tip, tested{by,date,score,status}
  prompt.md   the text people copy (or skill/ for a skill: SKILL.md + files, zipped at build time)
  TEST.md     internal test notes (inputs, runs, limits) — kept in the repo, not shown on the site
Short links: /<n> → /p/<n>/ (the number printed on the carousel).
"""
import html
import json
import re
import shutil
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
REPO = "https://github.com/BigS0MA/safi"
KIND = {"prompt": "برومبت", "trick": "حيلة", "skill": "سكيل", "block": "إعدادات", "guide": "دليل"}
MONTHS = ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول",
          "تشرين الأول", "تشرين الثاني", "كانون الأول"]


def ar_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def e(s):
    return html.escape(str(s or ""))


def rich(s):
    """escape, keep Latin runs in order, «الـ AI» together."""
    s = e(s)
    s = re.sub(r"(?<![&A-Za-z0-9])([A-Za-z][A-Za-z0-9 .'’|/+\-]*[A-Za-z0-9])", r"<bdi>\1</bdi>", s)
    s = re.sub(r"(الـ|ال) (<bdi>)", r"\1&nbsp;\2", s)
    return re.sub(r"!([\u0600-\u06FF]+)", r'<bdi class="cmd" dir="rtl">!\1</bdi>', s)   # «!لخص» stays one unit


def prompt_html(text):
    """the copy box: [placeholders] marked so people see what to fill."""
    return re.sub(r"\[([^\]\n]+)\]", r'<mark>[\1]</mark>', e(text.strip()))


CSS = """
@font-face{font-family:Plex;src:url(/fonts/plex-arabic-regular.woff2) format('woff2');font-weight:400;font-display:swap}
@font-face{font-family:Plex;src:url(/fonts/plex-arabic-bold.woff2) format('woff2');font-weight:700;font-display:swap}
@font-face{font-family:Mono;src:url(/fonts/plex-mono-500.woff2) format('woff2');font-weight:500;font-display:swap}
@font-face{font-family:Mono;src:url(/fonts/plex-mono-700.woff2) format('woff2');font-weight:700;font-display:swap}
:root{--paper:#F2EFE8;--ink:#141414;--sig:#FF5A1F;--grid:rgba(201,196,184,.55);--mute:#5E5A52;--line:#C9C4B8;--card:#FBF8F1}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%}
body{background:var(--paper);background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);
  background-size:36px 36px;color:var(--ink);font-family:Plex,system-ui,sans-serif;font-size:18px;line-height:1.7;direction:rtl;min-height:100vh}
a{color:inherit}
bdi{unicode-bidi:isolate}
.cmd{white-space:nowrap;font-weight:700}
.wrap{max-width:760px;margin:0 auto;padding:0 16px}
.top{display:flex;justify-content:space-between;align-items:center;padding:22px 0}
.brand{font-family:Mono;font-weight:500;font-size:15px;direction:ltr;text-decoration:none}
.chip{font-family:Mono;font-weight:700;font-size:13px;color:var(--sig);border:2px solid var(--sig);padding:3px 10px;background:var(--paper);direction:ltr;display:inline-block;letter-spacing:.04em}
.chip.ar{font-family:Plex;direction:rtl;letter-spacing:0}
.chip.ink{color:var(--ink);border-color:var(--ink)}
h1{font-size:clamp(40px,9vw,72px);line-height:1.12;font-weight:700;margin:28px 0 14px;text-wrap:balance}
h2{font-size:24px;line-height:1.3;margin:0 0 14px}
.lede{font-size:20px;color:#2B2926;max-width:36em;text-wrap:pretty}
.hot{text-decoration:underline;text-decoration-color:var(--sig);text-decoration-thickness:.12em;text-underline-offset:.18em}
section{margin:44px 0}
.go{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:26px;font-size:16px}
.go input{font-family:Mono;font-size:18px;width:84px;padding:8px 10px;border:2px solid var(--ink);background:#fff;text-align:center;direction:ltr}
.go button,.btn{font-family:Plex;font-weight:700;font-size:16px;background:var(--ink);color:var(--paper);border:0;padding:10px 18px;cursor:pointer;text-decoration:none;display:inline-block}
.list{display:grid;gap:18px}
.card{display:grid;grid-template-columns:auto 1fr;gap:4px 20px;background:var(--card);border:2px solid var(--ink);padding:20px 22px;text-decoration:none;box-shadow:6px 6px 0 var(--ink);transition:transform .12s,box-shadow .12s}
.card:hover,.card:focus-visible{transform:translate(-2px,-2px);box-shadow:8px 8px 0 var(--sig);outline:none}
.card .n{font-family:Mono;font-weight:700;font-size:44px;line-height:1;color:var(--sig);direction:ltr;grid-row:span 3}
.card .t{font-weight:700;font-size:21px;line-height:1.35}
.card .h{font-size:16px;color:var(--mute);line-height:1.6}
.card .m{display:flex;gap:8px;align-items:center;margin-top:6px;flex-wrap:wrap}
.num{font-family:Mono;font-weight:700;font-size:64px;line-height:1;color:var(--sig);direction:ltr;display:inline-block;margin-top:10px}
.steps{list-style:none;counter-reset:s;display:grid;gap:12px}
.steps li{counter-increment:s;display:flex;gap:14px;align-items:flex-start}
.steps li::before{content:counter(s);flex:none;width:34px;height:34px;display:grid;place-items:center;background:var(--ink);color:var(--paper);font-family:Mono;font-weight:700;font-size:16px;margin-top:2px}
.pbox{background:#fff;border:3px solid var(--ink);box-shadow:8px 8px 0 var(--ink)}
.pbox .bar{display:flex;justify-content:space-between;align-items:center;background:var(--ink);color:var(--paper);padding:8px 8px 8px 14px;direction:ltr}
.pbox .bar span{font-family:Mono;font-size:13px;letter-spacing:.08em}
.pbox .bar span.ar{font-family:Plex;font-size:14px;letter-spacing:0;direction:rtl}
.copy{font-family:Plex;font-weight:700;font-size:15px;background:var(--sig);color:var(--ink);border:0;padding:6px 16px;cursor:pointer;direction:rtl}
.copy.done{background:var(--paper)}
.pbox pre{unicode-bidi:plaintext;font-family:Plex;font-size:17px;line-height:1.85;white-space:pre-wrap;word-wrap:break-word;padding:20px 20px 24px;direction:rtl;text-align:right}
mark{background:#FFE3D6;color:var(--ink);padding:0 3px;border-bottom:2px solid var(--sig)}
.hint{font-size:15px;color:var(--mute);margin-top:14px}
.tape{background:var(--card);padding:18px 22px;transform:rotate(-.6deg);box-shadow:0 2px 0 rgba(0,0,0,.06),0 10px 22px rgba(0,0,0,.07);font-size:17px}
.tape b{display:block;font-size:15px;color:var(--sig);margin-bottom:4px}
.shot{max-width:100%;border:2px solid var(--ink);margin-top:16px;background:#fff}
.nav{display:flex;justify-content:space-between;gap:12px;margin:48px 0 0;font-size:16px}
.nav a{text-decoration:none;font-weight:700}
footer{margin:64px 0 0;padding:24px 0 40px;border-top:2px solid var(--ink);font-size:14px;color:var(--mute);display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
footer .brand{color:var(--ink)}
.skip{position:absolute;right:-9999px}.skip:focus{right:16px;top:8px;background:#fff;padding:6px}
@media (max-width:520px){body{font-size:17px}.nav{flex-direction:column}.nav a:last-child{align-self:flex-end}.card{grid-template-columns:1fr}.card .n{grid-row:auto;font-size:36px}}
"""

JS = """
document.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',async()=>{
  const t=document.getElementById(b.dataset.for).innerText;
  try{await navigator.clipboard.writeText(t)}catch(e){const r=document.createRange();r.selectNodeContents(document.getElementById(b.dataset.for));
    const s=getSelection();s.removeAllRanges();s.addRange(r);document.execCommand('copy');s.removeAllRanges()}
  b.textContent='انتسخ ✓';b.classList.add('done');setTimeout(()=>{b.textContent='انسخ';b.classList.remove('done')},1800)}));
const g=document.getElementById('go');if(g)g.addEventListener('submit',ev=>{ev.preventDefault();
  const n=parseInt(document.getElementById('gon').value,10);if(n>0)location.href='/p/'+n+'/'});
"""


def page(title, desc, body, path="/"):
    return f"""<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website"><meta property="og:image" content="https://safi.motasem.ai/og.png"><meta property="og:locale" content="ar_JO">
<meta name="theme-color" content="#F2EFE8">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/plex-arabic-bold.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style></head>
<body><a class="skip" href="#main">تخطّى للمحتوى</a>
<div class="wrap">
<header class="top"><a class="brand" href="/">motasem.ai</a><a class="chip ar" href="/" style="text-decoration:none">صافي</a></header>
<main id="main">{body}</main>
<footer><span>لقيت غلط أو عندك فكرة لعنصر جاي؟ احكيلي على انستغرام.</span><a class="brand" href="{REPO}">GitHub ↗</a></footer>
</div><script>{JS}</script></body></html>"""


def load_items():
    items = []
    for d in sorted((ROOT / "items").iterdir()):
        f = d / "item.json"
        if not f.exists():
            continue
        it = json.loads(f.read_text(encoding="utf-8"))
        it["_dir"] = d
        p = d / "prompt.md"
        it["_prompt"] = p.read_text(encoding="utf-8") if p.exists() else ""
        it["_skill"] = (d / "skill").is_dir()
        items.append(it)
    return sorted(items, key=lambda x: x["n"])


def item_page(it, prev, nxt):
    n, d = it["n"], it["_dir"]
    out = SITE / "p" / str(n)
    out.mkdir(parents=True, exist_ok=True)
    B = [f'<span class="num">{n:02d}</span> <span class="chip ar">{KIND.get(it["kind"], "")}</span>',
         f'<h1>{rich(it["title"])}</h1><p class="lede">{rich(it["hook"])}</p>']
    if it.get("how"):
        B.append(f'<section><h2>{rich(it.get("how_title", "كيف تستخدمه"))}</h2><ol class="steps">'
                 + "".join(f"<li><span>{rich(x)}</span></li>" for x in it["how"]) + "</ol>")
        if it["_skill"]:
            z = out / f'{it["slug"]}.zip'
            with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in sorted((d / "skill").rglob("*")):
                    if f.is_file() and "__pycache__" not in f.parts:
                        zf.write(f, Path(it["slug"]) / f.relative_to(d / "skill"))
            B.append(f'<p style="margin-top:22px"><a class="btn" href="{z.name}" download>نزّل السكيل (.zip)</a></p>')
        B.append("</section>")
    if it["_prompt"]:
        label = '<span class="ar">' + e(it.get("prompt_label", "انسخه كامل")) + "</span>"
        head = f'<h2>{rich(it["prompt_title"])}</h2>' if it.get("prompt_title") else ""
        B.append(f'<section>{head}<div class="pbox"><div class="bar"><button class="copy" data-for="p{n}">انسخ</button>{label}</div>'
                 f'<pre id="p{n}">{prompt_html(it["_prompt"])}</pre></div>'
                 + ('<p class="hint">عبّي الأماكن الملوّنة، والباقي خليه زي ما هو.</p>' if "[" in it["_prompt"] else "") + "</section>")
    for sec in it.get("sections", []):
        inner = (('<ol class="steps">' + "".join(f"<li><span>{rich(x)}</span></li>" for x in sec["steps"]) + "</ol>") if sec.get("steps")
                 else f'<p>{rich(sec.get("text", ""))}</p>')
        B.append(f'<section><h2>{rich(sec["title"])}</h2>{inner}</section>')
    shot = next((f for f in d.glob("result.*") if f.suffix.lower() in (".png", ".jpg", ".webp")), None)
    if shot:
        shutil.copy(shot, out / shot.name)
        B.append(f'<section><img class="shot" src="{shot.name}" alt="مثال على النتيجة" loading="lazy"></section>')
    if it.get("tip"):
        B.append(f'<section><div class="tape"><b>نصيحة</b>{rich(it["tip"])}</div></section>')
    nav = '<nav class="nav">' + (f'<a href="/p/{prev["n"]}/">→ {prev["n"]:02d} {rich(prev["title"])}</a>' if prev else "<span></span>") \
        + (f'<a href="/p/{nxt["n"]}/">{nxt["n"]:02d} {rich(nxt["title"])} ←</a>' if nxt else '<a href="/">كل المكتبة ←</a>') + "</nav>"
    B.append(nav)
    (out / "index.html").write_text(page(f'{it["title"]} · صافي', it["hook"], "".join(B), f"/p/{n}/"), encoding="utf-8")


def index_page(items):
    cards = "".join(
        f'<a class="card" href="/p/{it["n"]}/"><span class="n">{it["n"]:02d}</span>'
        f'<span class="t">{rich(it["title"])}</span><span class="h">{rich(it["hook"])}</span>'
        f'<span class="m"><span class="chip ar ink">{KIND.get(it["kind"], "")}</span></span></a>'
        for it in items)
    body = ('<h1>انسخ، نزّل، <span class="hot">واشتغل</span>.</h1>'
            '<p class="lede">برومبتات وسكيلز لشغلك بالعربي، من كاروسيلات motasem.ai. كل وحدة بكبسة نسخ أو تنزيل.</p>'
            '<form class="go" id="go"><label for="gon">عندك رقم من كاروسيل؟</label><input id="gon" inputmode="numeric" placeholder="01" aria-label="رقم الكاروسيل"><button>افتح</button></form>'
            f'<section class="list" aria-label="المكتبة">{cards}</section>')
    (SITE / "index.html").write_text(page("صافي · motasem.ai", "برومبتات وسكيلز لشغلك بالعربي، بكبسة نسخ أو تنزيل.", body), encoding="utf-8")


def main():
    items = load_items()
    shutil.rmtree(SITE / "p", ignore_errors=True)
    for i, it in enumerate(items):
        item_page(it, items[i - 1] if i else None, items[i + 1] if i + 1 < len(items) else None)
    index_page(items)
    (SITE / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" fill="#FF5A1F"/>'
        '<rect x="7" y="7" width="18" height="18" fill="none" stroke="#141414" stroke-width="3"/></svg>', encoding="utf-8")
    redirects = "\n".join(f'/{it["n"]}  /p/{it["n"]}/  301' for it in items)
    (SITE / "_redirects").write_text(redirects + "\n", encoding="utf-8")
    (SITE / "404.html").write_text(page("مش موجود · صافي", "", '<h1>هالرقم <span class="hot">مش موجود</span> لسا.</h1>'
                                        '<p class="lede">يمكن الكاروسيل لسا ما نزل. <a href="/">شوف كل المكتبة</a>.</p>'), encoding="utf-8")
    print(f"✅ {len(items)} عنصر → {SITE}")


if __name__ == "__main__":
    main()
