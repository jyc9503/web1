#!/usr/bin/env python3
"""spec.md -> spec.html 변환기.

사용:
  python3 tools/build_spec.py plans/<슬러그>
  python3 tools/build_spec.py plans/<슬러그> --artifact /경로/artifact.html

- 원본은 항상 spec.md. HTML은 이 스크립트로만 만든다.
- 디자인은 .claude/skills/plan-doc/assets/spec-sample.html 의 CSS를 그대로 가져온다.
- spec.md 규칙:
  * 맨 위 --- 사이에 title / subtitle / version / author / target / game
  * `## 제목` 하나가 섹션 하나 (목차·번호 자동)
  * 표 셀에 {확정} {검증필요} {미정} 을 쓰면 배지가 되고 행에 상태가 붙는다
  * 첫 열이 R-01, T-03 같은 ID면 ID 서식 + 상단 건수 집계 대상
  * `[[svg:파일명.svg]]` 한 줄이면 같은 폴더의 SVG를 흐름도로 삽입
  * `> ` 인용은 전달사항 박스
- --artifact 를 주면 Artifact 게시용 조각(doctype·head 없음)을 따로 쓴다.
"""
import argparse
import pathlib
import re
import sys

try:
    import markdown
except ImportError:
    sys.exit("python 'markdown' 패키지가 필요합니다: pip install markdown")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAMPLE = ROOT / ".claude/skills/plan-doc/assets/spec-sample.html"
BADGES = {"확정": ("ok", "b-ok"), "검증필요": ("warn", "b-warn"), "미정": ("tbd", "b-tbd")}
TOKEN = re.compile(r"\{(확정|검증필요|미정)\}")
ID_RE = re.compile(r"^[A-Z]{1,3}-\d+$")

EXTRA_CSS = """
main ul,main ol{margin:0 0 14px;padding-left:22px;max-width:68ch}
main li{margin:3px 0}
main pre{margin:12px 0 16px;padding:14px 16px;background:var(--surface);border:1px solid var(--line);border-radius:8px;overflow-x:auto;font:13px/1.6 var(--f-mono)}
main pre code{background:none;color:var(--ink);padding:0;font-size:inherit}
.tablewrap{margin:12px 0 18px}
.flow{margin:12px 0 18px}
.note ul{margin:8px 0 0}
.note p{margin:0}
td code{white-space:nowrap}
"""

SCRIPT = """(function(){
  var b=document.getElementById('vbtn');
  if(!b)return;
  b.addEventListener('click',function(){
    var on=b.getAttribute('aria-pressed')!=='true';
    b.setAttribute('aria-pressed',on);
    document.querySelector('main').classList.toggle('only-verify',on);
  });
})();"""


def parse_front(text):
    meta = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return meta, text
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[m.end():]


def process_rows(html_text, stats):
    def row(m):
        body = m.group(1)
        if "<th" in body:
            return m.group(0)
        tokens = TOKEN.findall(body)
        attrs = ""
        if tokens:
            state = BADGES[tokens[0]][0]
            attrs = f' data-s="{state}"'
            body = TOKEN.sub(lambda t: f'<span class="badge {BADGES[t.group(1)][1]}">{t.group(1)}</span>', body)
        cells = re.findall(r"<td[^>]*>(.*?)</td>", body, re.S)
        if cells and ID_RE.match(re.sub(r"<[^>]+>", "", cells[0]).strip()):
            body = re.sub(r"<td([^>]*)>", r'<td class="id"\1>', body, count=1)
            if tokens and BADGES[tokens[0]][0] in ("warn", "tbd"):
                stats["verify"] += 1
        return f"<tr{attrs}>{body}</tr>"

    return re.sub(r"<tr>(.*?)</tr>", row, html_text, flags=re.S)


def convert(md_text, plan_dir):
    meta, body = parse_front(md_text)
    body = re.sub(r"^\[\[svg:(.+?)\]\]\s*$", r"@@SVG:\1@@", body, flags=re.M)
    html_body = markdown.markdown(body, extensions=["tables", "fenced_code"])

    html_body = html_body.replace(' style="text-align: right;"', ' class="num"')
    stats = {"verify": 0}
    html_body = process_rows(html_body, stats)
    html_body = re.sub(r"<table>", '<div class="tablewrap"><table>', html_body)
    html_body = html_body.replace("</table>", "</table></div>")

    def svg(m):
        data = (plan_dir / m.group(1)).read_text(encoding="utf-8")
        return f'<div class="flow">{data}</div>'

    html_body = re.sub(r"<p>@@SVG:(.+?)@@</p>", svg, html_body)
    html_body = re.sub(r"<blockquote>\s*(.*?)\s*</blockquote>", r'<div class="note dev">\1</div>', html_body, flags=re.S)

    chunks = re.split(r"(?=<h2>)", html_body)
    sections, toc = [], []
    n = 0
    for chunk in chunks:
        m = re.match(r"<h2>(.*?)</h2>(.*)", chunk, re.S)
        if not m:
            continue
        n += 1
        title, rest = m.group(1), m.group(2)
        if "검증" in title or "미결" in title:
            rest = rest.replace("<ul>", '<ul class="check">')
            rest = re.sub(r"<li>(.*?)</li>", r'<li><span class="mono">□</span><span>\1</span></li>', rest, flags=re.S)
        sections.append(f'<section id="s{n}"><h2><span class="sec">§{n}</span>{title}</h2>{rest}</section>')
        toc.append(f'<a href="#s{n}">{re.sub(r"<[^>]+>", "", title)}</a>')

    return meta, stats["verify"], "\n".join(sections), "\n".join(toc)


def build(plan_dir):
    plan_dir = pathlib.Path(plan_dir)
    meta, verify_count, sections, toc = convert((plan_dir / "spec.md").read_text(encoding="utf-8"), plan_dir)
    sample = SAMPLE.read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", sample, re.S).group(1) + EXTRA_CSS
    font = re.search(r'<link rel="stylesheet" href="https://fonts[^>]*>', sample).group(0)

    title = meta.get("title", "기획서")
    page = f"""<div class="shell">
  <nav class="toc" aria-label="목차">
    <p class="label">목차</p>
    {toc}
    <div class="legend">
      <span><span class="badge b-ok">확정</span> 그대로 구현</span>
      <span><span class="badge b-warn">검증필요</span> 회사 데이터 확인 전</span>
      <span><span class="badge b-tbd">미정</span> 결정 대기</span>
    </div>
    <button class="vbtn" id="vbtn" type="button" aria-pressed="false">검증필요·미정만 강조</button>
  </nav>
  <main>
    <header class="doc">
      <span class="sample-tag">{meta.get("game", "")} · 초안</span>
      <h1>{title}</h1>
      <p class="sub">{meta.get("subtitle", "")}</p>
      <dl class="meta">
        <div><dt>버전</dt><dd class="mono">{meta.get("version", "")}</dd></div>
        <div><dt>작성</dt><dd>{meta.get("author", "")}</dd></div>
        <div><dt>구현 대상</dt><dd>{meta.get("target", "")}</dd></div>
        <div><dt>검증필요·미정 (ID 기준)</dt><dd><span class="badge b-warn">{verify_count}건</span></dd></div>
      </dl>
    </header>
    {sections}
  </main>
</div>
<script>{SCRIPT}</script>"""

    standalone = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
{font}
<style>
body{{margin:0}}
{css}
</style>
</head>
<body>
{page}
</body>
</html>
"""
    fragment = f"""<title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
{font}
<style>
{css}
</style>
{page}
"""
    return standalone, fragment, verify_count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan_dir")
    ap.add_argument("--artifact", help="Artifact 게시용 조각 HTML을 쓸 경로")
    args = ap.parse_args()
    standalone, fragment, count = build(args.plan_dir)
    out = pathlib.Path(args.plan_dir) / "spec.html"
    out.write_text(standalone, encoding="utf-8")
    print(f"wrote {out} (검증필요·미정 {count}건)")
    if args.artifact:
        pathlib.Path(args.artifact).write_text(fragment, encoding="utf-8")
        print(f"wrote {args.artifact}")


if __name__ == "__main__":
    main()
