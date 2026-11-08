#!/usr/bin/env python3
"""화면 시안(mockups/index.html)과 한 장 요약(summary.html)을 만든다.

사용: python3 plans/story-map-pin-move/src/gen_visuals.py
- 장면 데이터는 프로토타입(proto/index.html)의 예시와 같다. 한쪽을 바꾸면 다른 쪽도 맞춘다.
- 상태 건수는 spec.md 에서 직접 센다.
"""
import math
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent.parent
W, H = 640, 360
ASPECT = 16 / 9
INTRO, PINFADE = 0.4, 0.4
COL = {"char_a": "#e2576b", "char_b": "#3d8bfd", "char_c": "#35b37e"}
NAME = {"char_a": "전투원 A", "char_b": "전투원 B", "char_c": "전투원 C"}
PLACES = [("정거장", .10, .74), ("관측소", .78, .30), ("북문", .14, .30), ("광장", .62, .50),
          ("숲", .88, .80), ("항구", .84, .52), ("탑", .45, .16)]
R = 14.5
FONT = 'font-family="Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif"'


def pin(c, path, delay=0.0, dur=2.0, curve="smooth"):
    return dict(c=c, path=path, delay=delay, dur=dur, curve=curve)


S1 = [pin("char_a", [(.10, .74), (.28, .56), (.50, .62), (.78, .30)], 0, 2.4),
      pin("char_b", [(.14, .30), (.40, .36), (.62, .50)], 0.6, 2.0),
      pin("char_c", [(.88, .80), (.66, .74), (.84, .52)], 1.4, 1.8, "line")]
S2 = [pin("char_a", [(.78, .30), (.70, .18), (.45, .16)], 0, 2.0),
      pin("char_b", [(.62, .50), (.70, .68), (.88, .80)], 0.6, 2.0),
      pin("char_c", [(.84, .52)], 0, 2.0, "line")]


def sample(p):
    pts = p["path"]
    if len(pts) < 3 or p["curve"] == "line":
        return list(pts)
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(len(pts) - 1, i + 2)]
        for s in range(16):
            u = s / 16
            u2, u3 = u * u, u * u * u
            f = lambda a, b, c, d: .5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u2 + (-a + 3 * b - 3 * c + d) * u3)
            out.append((f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1])))
    out.append(pts[-1])
    return out


def lens(pts):
    L = [0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.hypot(pts[i][0] - pts[i - 1][0], (pts[i][1] - pts[i - 1][1]) / ASPECT))
    return L


def at(pts, L, f):
    if len(pts) == 1 or L[-1] == 0:
        return pts[0][0], pts[0][1], 0, 1
    d = f * L[-1]
    i = 1
    while i < len(L) - 1 and L[i] < d:
        i += 1
    seg = L[i] - L[i - 1]
    k = (d - L[i - 1]) / seg if seg else 0
    a, b = pts[i - 1], pts[i]
    return a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, math.atan2(b[1] - a[1], (b[0] - a[0]) * ASPECT), i


def ease(u):
    return 2 * u * u if u < .5 else 1 - (-2 * u + 2) ** 2 / 2


def xy(q):
    return f"{q[0] * W:.1f},{q[1] * H:.1f}"


def poly(pts, col, width, dash, alpha):
    if len(pts) < 2:
        return ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{" ".join(xy(q) for q in pts)}" fill="none" stroke="{col}" stroke-width="{width}"'
            f' stroke-linecap="round" stroke-linejoin="round"{d} opacity="{alpha}"/>')


DOT = (2.4, "0.1 5.5")  # 궤적 점선


def bg():
    o = ('<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1a2233"/>'
         '<stop offset="1" stop-color="#10141f"/></linearGradient></defs>'
         f'<rect width="{W}" height="{H}" fill="url(#g)"/>')
    for i in range(21):
        o += f'<line x1="{i / 20 * W:.1f}" y1="0" x2="{i / 20 * W:.1f}" y2="{H}" stroke="rgba(140,160,200,.10)"/>'
    for i in range(13):
        o += f'<line x1="0" y1="{i / 12 * H:.1f}" x2="{W}" y2="{i / 12 * H:.1f}" stroke="rgba(140,160,200,.10)"/>'
    for cx, cy, rx, ry, col in [(.18, .62, .16, .2, '#1f2c3f'), (.5, .55, .14, .26, '#222f45'), (.82, .34, .14, .2, '#1d2a3d'),
                                (.3, .26, .12, .16, '#1e293b'), (.78, .78, .12, .14, '#1f2b3e')]:
        o += f'<ellipse cx="{cx * W}" cy="{cy * H}" rx="{rx * W}" ry="{ry * H}" fill="{col}" stroke="rgba(150,170,210,.18)"/>'
    o += f'<text x="{W / 2}" y="{H * .965}" text-anchor="middle" font-size="8" font-weight="600" fill="rgba(160,175,205,.4)">배경 리소스 자리 (예시)</text>'
    return o


def places():
    o = ""
    for name, x, y in PLACES:
        X, Y = x * W, y * H
        o += (f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="2.6" fill="#f4f1e8" stroke="rgba(8,10,16,.9)" stroke-width="1.5"/>'
              f'<text x="{X:.1f}" y="{Y - R - 6:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="#f4f1e8"'
              f' stroke="rgba(8,10,16,.85)" stroke-width="3" paint-order="stroke" stroke-linejoin="round">{name}</text>')
    return o


def pinsvg(c, x, y, ang=None, alpha=1.0, selected=False):
    X, Y = x * W, y * H
    o = (f'<g opacity="{alpha}"><circle cx="{X:.1f}" cy="{Y:.1f}" r="{R}" fill="{COL[c]}" stroke="#fff" stroke-width="2.5"/>'
         f'<text x="{X:.1f}" y="{Y + R * .36:.1f}" text-anchor="middle" font-size="{R:.1f}" font-weight="700" fill="#fff">{NAME[c][-1]}</text>')
    if ang is not None:
        o += f'<g transform="translate({X:.1f} {Y:.1f}) rotate({math.degrees(ang):.1f})"><path d="M{R + 8} 0L{R + 1} -5L{R + 1} 5Z" fill="#fff"/></g>'
    tw = len(NAME[c]) * 7.4 + 10
    o += (f'<rect x="{X - tw / 2:.1f}" y="{Y + R + 4:.1f}" width="{tw:.1f}" height="16" rx="8" fill="rgba(8,10,16,.8)"/>'
          f'<text x="{X:.1f}" y="{Y + R + 15.5:.1f}" text-anchor="middle" font-size="10" fill="#f1f3f8">{NAME[c]}</text></g>')
    if selected:
        o += f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{R + 5}" fill="none" stroke="#fff" stroke-width="1.5" stroke-dasharray="4 4"/>'
    return o


def svg_open(label):
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{label}" xmlns="http://www.w3.org/2000/svg" {FONT}>'


def game(scene, t, prev=None, seamless=False, dialog=True):
    """게임 보기: 지나온 구간만 점선, 앞으로 갈 경로·도착 지점 없음."""
    base = 0 if seamless else INTRO + PINFADE
    o = svg_open(f"게임 화면 {t}초") + bg() + places()
    for c, pts in (prev or []):
        o += poly(pts, COL[c], DOT[0], DOT[1], .4)
    st = []
    for p in scene:
        pts = sample(p)
        L = lens(pts)
        moving = len(p["path"]) > 1
        loc = max(0, min(1, round((t - base - p["delay"]) / p["dur"], 6))) if moving else 1
        x, y, a, i = at(pts, L, ease(loc))
        st.append((p, pts, loc, x, y, a, i, moving))
    for p, pts, loc, x, y, a, i, moving in st:
        if moving and loc > 0:
            o += poly(pts[:i] + [(x, y)], COL[p["c"]], DOT[0], DOT[1], .95)
    for p, pts, loc, x, y, a, i, moving in st:
        o += pinsvg(p["c"], x, y, a if 0 < loc < 1 else None)
    if dialog:
        o += ('<rect x="26" y="300" width="588" height="44" rx="8" fill="none" stroke="rgba(255,255,255,.3)" stroke-dasharray="4 4"/>'
              '<text x="320" y="326" text-anchor="middle" font-size="10" fill="rgba(255,255,255,.45)">대사창 자리 · 연출 중 숨김 (R-15)</text>')
    return o + "</svg>"


def edit(scene, sel=0, prev=None):
    """편집 보기: 앞으로 갈 경로(파선), 도착 링, 선택한 핀의 점 번호."""
    o = svg_open("툴 편집 화면") + bg() + places()
    for c, pts in (prev or []):
        o += poly(pts, COL[c], DOT[0], DOT[1], .4)
    for k, p in enumerate(scene):
        pts = sample(p)
        on = k == sel
        o += poly(pts, COL[p["c"]], 2.2 if on else 1.8, "7 5", .95 if on else .45)
        if len(p["path"]) > 1:
            ex, ey = pts[-1]
            o += f'<circle cx="{ex * W:.1f}" cy="{ey * H:.1f}" r="{R * .55:.1f}" fill="none" stroke="{COL[p["c"]]}" stroke-width="2.2" opacity="{1 if on else .45}"/>'
    p = scene[sel]
    for n, q in enumerate(p["path"]):
        if n == 0:
            continue
        o += (f'<circle cx="{q[0] * W:.1f}" cy="{q[1] * H:.1f}" r="6.5" fill="#0e1118" stroke="{COL[p["c"]]}" stroke-width="2.2"/>'
              f'<text x="{q[0] * W:.1f}" y="{q[1] * H + 3:.1f}" text-anchor="middle" font-size="7.5" font-weight="700" fill="{COL[p["c"]]}">{n + 1}</text>')
    for k, p2 in enumerate(scene):
        o += pinsvg(p2["c"], p2["path"][0][0], p2["path"][0][1], None, 1 if k == sel else .75, k == sel)
    o += ('<rect x="10" y="10" width="118" height="20" rx="4" fill="rgba(10,12,18,.7)"/>'
          '<text x="18" y="24" font-size="9.5" fill="#c3cbdb">편집 보기 · 전투원 A 선택</text>')
    return o + "</svg>"


PREV = [(p["c"], sample(p)) for p in S1]


def anatomy():
    o = f'<svg viewBox="0 0 560 300" role="img" aria-label="핀과 장소 마크의 구성 요소 해부도" xmlns="http://www.w3.org/2000/svg" {FONT}>'
    o += '<rect width="560" height="300" rx="10" fill="#141a27"/>'
    o += '<polyline points="40,270 110,248 175,236" fill="none" stroke="#e2576b" stroke-width="4" stroke-linecap="round" stroke-dasharray="0.1 9" opacity=".4"/>'
    o += '<polyline points="175,236 240,205 290,175 330,150" fill="none" stroke="#e2576b" stroke-width="5" stroke-linecap="round" stroke-dasharray="0.1 11"/>'
    o += ('<circle cx="470" cy="96" r="5" fill="#f4f1e8" stroke="rgba(8,10,16,.9)" stroke-width="2"/>'
          '<text x="470" y="74" text-anchor="middle" font-size="18" font-weight="700" fill="#f4f1e8" stroke="rgba(8,10,16,.85)" stroke-width="5" paint-order="stroke">관측소</text>')
    x, y, r = 330, 150, 44
    o += f'<circle cx="{x}" cy="{y}" r="{r}" fill="#e2576b" stroke="#fff" stroke-width="5"/><text x="{x}" y="{y + 16}" text-anchor="middle" font-size="44" font-weight="700" fill="#fff">A</text>'
    o += f'<g transform="translate({x} {y}) rotate(-35)"><path d="M{r + 24} 0L{r + 3} -14L{r + 3} 14Z" fill="#fff"/></g>'
    o += f'<rect x="{x - 50}" y="{y + r + 10}" width="100" height="26" rx="13" fill="rgba(8,10,16,.8)"/><text x="{x}" y="{y + r + 28}" text-anchor="middle" font-size="14" fill="#f1f3f8">전투원 A</text>'

    def call(n, px, py, tx, ty):
        return (f'<line x1="{px}" y1="{py}" x2="{tx}" y2="{ty}" stroke="#9aa6bd" stroke-width="1"/>'
                f'<circle cx="{tx}" cy="{ty}" r="10" fill="#2f55d4"/><text x="{tx}" y="{ty + 4}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">{n}</text>')
    o += call(1, 392, 108, 420, 150)
    o += call(2, x - 26, y - 30, x - 90, y - 78)
    o += call(3, x - r, y, x - 116, y - 24)
    o += call(4, x, y + r + 23, x - 96, y + r + 42)
    o += call(5, 240, 205, 220, 260)
    o += call(6, 470, 96, 520, 140)
    o += call(7, 110, 248, 92, 214)
    return o + "</svg>"


def counts():
    t = (HERE / "spec.md").read_text(encoding="utf-8")
    c = {"확정": 0, "검증필요": 0, "미정": 0}
    for line in t.splitlines():
        if re.match(r"\| [A-Z]{1,3}-\d+ \|", line):
            m = re.search(r"\{(확정|검증필요|미정)\}", line)
            if m:
                c[m.group(1)] += 1
    return c


TOKENS = """
:root{
  --bg:#f4f5f8; --surface:#ffffff; --ink:#161b26; --muted:#586174; --line:#dde1e9;
  --accent:#2f55d4; --accent-soft:#e7ecfc;
  --ok:#157347; --ok-soft:#dcf2e6; --warn:#8f5500; --warn-soft:#fdebc8; --tbd:#5f43b2; --tbd-soft:#ebe5fa;
  --f-body:"Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;
  --f-mono:"JetBrains Mono",ui-monospace,Consolas,"D2Coding",monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#10131a; --surface:#171b24; --ink:#e8ebf2; --muted:#9aa3b5; --line:#2a303c;
  --accent:#8fa8ff; --accent-soft:#1f2848;
  --ok:#62d49c; --ok-soft:#16332a; --warn:#f1bb5f; --warn-soft:#3a2c12; --tbd:#bba9f6; --tbd-soft:#2a2446; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#10131a; --surface:#171b24; --ink:#e8ebf2; --muted:#9aa3b5; --line:#2a303c;
  --accent:#8fa8ff; --accent-soft:#1f2848;
  --ok:#62d49c; --ok-soft:#16332a; --warn:#f1bb5f; --warn-soft:#3a2c12; --tbd:#bba9f6; --tbd-soft:#2a2446; color-scheme:dark}
*{box-sizing:border-box}
.badge{display:inline-block;font-size:11.5px;font-weight:700;line-height:1;padding:4px 8px;border-radius:999px;white-space:nowrap}
.b-ok{background:var(--ok-soft);color:var(--ok)}
.b-warn{background:var(--warn-soft);color:var(--warn)}
.b-tbd{background:var(--tbd-soft);color:var(--tbd)}
.tag{display:inline-block;font-size:11px;letter-spacing:.08em;color:var(--muted);border:1px dashed var(--muted);padding:1px 8px;border-radius:4px;margin-bottom:8px}
.mono{font-family:var(--f-mono);font-size:.88em;color:var(--muted)}
.shot{border-radius:10px;overflow:hidden;border:1px solid var(--line);background:#0e1118}
.shot svg{display:block;width:100%;height:auto}
"""

HEAD = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* {layout} */
{tokens}
{css}
</style>
</head>
<body>
"""


def mockups():
    cuts = [
        ("① 핀 등장", "장면 1 · 0.8초", game(S1, 0.8), "배경과 장소 마크가 보이고 핀이 시작 위치에 서 있다. 앞으로 갈 경로는 게임에서 보이지 않는다."),
        ("② 이동 중", "장면 1 · 2.3초", game(S1, 2.3), "핀이 지나온 구간만 점선으로 남는다. 이동 중인 핀에 진행 방향 삼각형이 붙는다."),
        ("③ 전원 도착", "장면 1 · 4.0초", game(S1, 4.0), "모든 핀이 장소에 도착했다. 도착 표시 없이 장소 마크로 위치를 읽는다. 1.0초 뒤 대사창이 돌아온다."),
        ("④ 이어가기", "장면 2 · 1.6초", game(S2, 1.6, PREV, True), "대사 뒤 장면 2가 장면 1의 끝 상태에서 바로 이어진다. 장면 1 궤적은 흐린 점선으로 남는다."),
    ]
    cards = "".join(f'<figure class="card"><div class="shot">{s}</div><figcaption><b>{n}</b> <span class="mono">{m}</span><p>{d}</p></figcaption></figure>' for n, m, s, d in cuts)
    css = """
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.7 var(--f-body);
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 64px}
.wrap{max-width:1120px;margin:0 auto}
h1{font-size:26px;line-height:1.3;margin:0 0 4px;text-wrap:balance}
h2{font-size:18px;margin:40px 0 6px}
h2+p{color:var(--muted);margin:0 0 12px}
p{margin:0 0 10px;max-width:68ch}
.sub{color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:16px}
.pair{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:16px}
.card{margin:0;min-width:0}
figcaption{padding-top:8px}
figcaption p{margin:2px 0 0;color:var(--muted);font-size:13.5px}
.two{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:20px;align-items:start}
@media (max-width:820px){.two{grid-template-columns:minmax(0,1fr)}}
.shot.ana{background:#141a27}
ol.legend{margin:0;padding-left:22px}
ol.legend li{margin:4px 0}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--surface)}
table{border-collapse:collapse;width:100%;min-width:560px;font-size:14px}
th{text-align:left;font-size:12px;color:var(--muted);letter-spacing:.06em;font-weight:500;padding:10px 14px;background:var(--bg);border-bottom:1px solid var(--line)}
td{padding:10px 14px;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:0}
td.spec{font-family:var(--f-mono);font-size:13px}
"""
    html = HEAD.format(title="맵 핀 이동 화면 시안", layout="Layout: 장면 컷 4장, 게임/편집 보기 비교, 해부도, 리소스 요청표를 위에서 아래로.", tokens=TOKENS, css=css)
    html += f"""<div class="wrap">
  <span class="tag">카제나 · 스토리 연출 · v0.2 시안</span>
  <h1>맵 핀 이동 화면 시안</h1>
  <p class="sub">아트팀과 배경 담당에게 보여주는 장면 컷과 리소스 요청 내용입니다. 배경, 캐릭터, 장소 이름은 자리표시용입니다. 스토리 화면의 실제 UI와 화면 방향은 확인 전이라 가로 16:9로 그렸습니다. <span class="badge b-warn">검증필요</span></p>

  <h2>장면 컷 (게임 화면)</h2>
  <p>장면 1과, 장면 1에서 이어가는 장면 2입니다.</p>
  <div class="grid">{cards}</div>

  <h2>게임 보기와 편집 보기</h2>
  <p>같은 장면 1입니다. 앞으로 갈 경로, 도착 링, 점 번호는 툴에서만 보입니다 (R-09).</p>
  <div class="pair">
    <figure class="card"><div class="shot">{game(S1, 4.0, dialog=False)}</div><figcaption><b>게임 보기</b><p>지나온 궤적(점선), 장소 마크, 핀만 보인다.</p></figcaption></figure>
    <figure class="card"><div class="shot">{edit(S1, 0)}</div><figcaption><b>편집 보기</b><p>모든 핀의 경로(파선)와 도착 링, 선택한 핀의 점 번호가 보인다.</p></figcaption></figure>
  </div>

  <h2>핀과 장소 마크 해부도</h2>
  <p>캐릭터 이름표(알약)와 장소 마크(글자 외곽선)는 모양을 다르게 해서 섞이지 않게 한다.</p>
  <div class="two">
    <div class="shot ana">{anatomy()}</div>
    <ol class="legend">
      <li><b>진행 방향 삼각형</b>: 이동 중에만 붙는다.</li>
      <li><b>핀 본체</b>: 캐릭터 얼굴 원형 아이콘, 흰 링, 지름은 화면 폭의 4.5%.</li>
      <li><b>핀 색</b>: 캐릭터마다 다른 색. 궤적도 같은 색이다.</li>
      <li><b>이름표</b>: 핀 아래 알약 모양, 어두운 반투명 바탕.</li>
      <li><b>지나온 궤적</b>: 둥근 점선. 앞으로 갈 경로는 그리지 않는다.</li>
      <li><b>장소 마크</b>: 작은 점과 장소 이름. 글자에 어두운 외곽선. 이름은 핀 높이만큼 위에 둔다.</li>
      <li><b>앞 장면 궤적</b>: 이어가기일 때 흐린 점선(40%)으로 남는다.</li>
    </ol>
  </div>

  <h2>리소스 요청</h2>
  <div class="tablewrap"><table>
    <thead><tr><th>리소스</th><th>규격</th><th>담당</th><th>상태</th></tr></thead>
    <tbody>
      <tr><td>배경 이미지</td><td class="spec">16:9 / 2048×1152 (추천)</td><td>배경</td><td><span class="badge b-tbd">미정</span></td></tr>
      <tr><td>장소 마크 세트</td><td class="spec">배경마다 장소 이름과 위치 목록</td><td>기획 또는 배경</td><td><span class="badge b-tbd">미정</span></td></tr>
      <tr><td>핀 얼굴 아이콘</td><td class="spec">원형 128×128, 기존 리소스 재사용 여부 확인</td><td>아트</td><td><span class="badge b-warn">검증필요</span></td></tr>
      <tr><td>핀 링 / 방향 삼각형</td><td class="spec">코드 도형. 아트 스타일 지정 시 이미지로 교체</td><td>아트</td><td><span class="badge b-warn">검증필요</span></td></tr>
      <tr><td>이름표 바탕</td><td class="spec">알약 9-slice, 높이 26px 기준</td><td>아트</td><td><span class="badge b-warn">검증필요</span></td></tr>
      <tr><td>장소 마크 점과 글꼴</td><td class="spec">점 아이콘 24×24 또는 코드 도형, 이름 글꼴과 외곽선 색</td><td>아트</td><td><span class="badge b-warn">검증필요</span></td></tr>
      <tr><td>궤적 점선</td><td class="spec">코드로 그림. 두께 4px, 간격 9px (1280px 기준)</td><td>-</td><td><span class="badge b-warn">검증필요</span></td></tr>
    </tbody>
  </table></div>
</div>
</body>
</html>
"""
    (HERE / "mockups" / "index.html").write_text(html, encoding="utf-8")


def summary():
    c = counts()
    css = """
body{margin:0;background:var(--bg);color:var(--ink);font:14.5px/1.65 var(--f-body);
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:24px 48px}
.wrap{max-width:1120px;margin:0 auto;display:grid;gap:18px}
.top{display:flex;flex-wrap:wrap;gap:10px 20px;align-items:end;justify-content:space-between}
h1{font-size:26px;line-height:1.3;margin:0;text-wrap:balance}
.one{margin:4px 0 0;color:var(--muted);max-width:62ch}
.counts{display:flex;gap:8px;flex-wrap:wrap}
.main{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:20px;align-items:start}
@media (max-width:860px){.main{grid-template-columns:minmax(0,1fr)}}
.cap{font-size:12.5px;color:var(--muted);margin:6px 0 0}
h2{font-size:12px;letter-spacing:.1em;color:var(--muted);font-weight:500;margin:0 0 8px}
.block{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px;min-width:0}
.col{display:grid;gap:14px;min-width:0}
ul.rules{list-style:none;margin:0;padding:0;display:grid;gap:6px}
ul.rules li{display:grid;grid-template-columns:52px minmax(0,1fr) auto;gap:10px;align-items:baseline}
.id{font-family:var(--f-mono);font-size:12px;color:var(--muted)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(88px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:8px;overflow:hidden}
.stats div{background:var(--surface);padding:8px 10px}
.stats b{display:block;font:600 20px/1.2 var(--f-mono);font-variant-numeric:tabular-nums}
.stats span{font-size:12px;color:var(--muted)}
.decide{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:12px}
.decide .block{padding:12px 14px}
.decide h3{font-size:14px;margin:0 0 4px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.decide p{margin:0;font-size:13px;color:var(--muted)}
.decide p b{color:var(--ink);font-weight:500}
"""
    html = HEAD.format(title="맵 핀 이동 연출 한 장 요약", layout="Layout: 한 화면 요약. 왼쪽 완성 컷, 오른쪽 규칙·수치, 아래 결정 필요.", tokens=TOKENS, css=css)
    html += f"""<div class="wrap">
  <header class="top">
    <div>
      <span class="tag">카제나 · 스토리 연출 · v0.2</span>
      <h1>맵 핀 이동 연출</h1>
      <p class="one">스토리 중 배경 지도 위에서 캐릭터 핀이 경로를 따라 움직여, 누가 어디서 어디로 갔는지 보여준다. 앞 연출이 끝난 자리에서 이어갈 수 있다.</p>
    </div>
    <div class="counts" aria-label="상태 집계 (규칙·툴 요구 ID 기준)"><span class="badge b-ok">확정 {c['확정']}</span><span class="badge b-warn">검증필요 {c['검증필요']}</span><span class="badge b-tbd">미정 {c['미정']}</span></div>
  </header>

  <div class="main">
    <div>
      <div class="shot">{game(S2, 2.6, PREV, True, dialog=False)}</div>
      <p class="cap">장면 2 완료 모습. 진한 점선은 이번 장면, 흐린 점선은 앞 장면 궤적. 배경과 캐릭터는 자리표시용.</p>
    </div>
    <div class="col">
      <section class="block">
        <h2>핵심 규칙</h2>
        <ul class="rules">
          <li><span class="id">R-01~03</span><span>배경 위 캐릭터 핀이 지정한 경로로 이동</span><span class="badge b-ok">확정</span></li>
          <li><span class="id">R-09</span><span>게임에는 지나온 구간만 점선. 앞 경로·도착 지점은 툴에서만</span><span class="badge b-ok">확정</span></li>
          <li><span class="id">R-20</span><span>배경 위 장소마다 이름 마크</span><span class="badge b-ok">확정</span></li>
          <li><span class="id">R-22</span><span>앞 연출 끝 상태에서 이어가기, 툴에서 버튼 하나로 가져옴</span><span class="badge b-ok">확정</span></li>
          <li><span class="id">R-12</span><span>재생 중 화면 탭하면 0.3초 만에 최종 상태</span><span class="badge b-warn">검증필요</span></li>
        </ul>
      </section>
      <section class="block">
        <h2>핵심 수치 <span class="badge b-warn" style="margin-left:6px">검증필요</span></h2>
        <div class="stats">
          <div><b>8</b><span>핀 최대</span></div>
          <div><b>12</b><span>핀당 점</span></div>
          <div><b>2.0s</b><span>기본 이동</span></div>
          <div><b>3~8s</b><span>총 길이</span></div>
        </div>
      </section>
      <section class="block">
        <h2>함께 보는 문서</h2>
        <ul class="rules">
          <li><span class="id">툴</span><span>「맵 이동 연출 편집 툴」: 경로 그리기, 장소 마크, 이어가기</span><span></span></li>
        </ul>
      </section>
    </div>
  </div>

  <section>
    <h2>결정이 필요합니다</h2>
    <div class="decide">
      <div class="block"><h3><span class="id">R-16</span>카메라 팬·줌 <span class="badge b-tbd">미정</span></h3><p><b>추천</b> 이번 버전은 화면 고정. 전체 지도가 보여야 위치가 읽힌다.</p></div>
      <div class="block"><h3><span class="id">R-17</span>핀 겹침 <span class="badge b-tbd">미정</span></h3><p><b>추천</b> 같은 지점에 도착하면 자동으로 살짝 어긋나게 배치.</p></div>
      <div class="block"><h3><span class="id">R-19</span>화면 맞춤 <span class="badge b-tbd">미정</span></h3><p><b>추천</b> 배경 전체가 보이게 맞추고 남는 곳은 여백. 규격은 16:9 2048×1152.</p></div>
      <div class="block"><h3><span class="id">R-30</span>효과음 <span class="badge b-tbd">미정</span></h3><p><b>추천</b> 이동 시작에만 짧은 효과음 1종, 핀이 여럿이어도 한 번.</p></div>
    </div>
  </section>
</div>
</body>
</html>
"""
    (HERE / "summary.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    mockups()
    summary()
    print("wrote mockups/index.html, summary.html", counts())
