# /// script
# dependencies = ["fonttools", "uharfbuzz"]
# ///
"""Build the profile README art: hero, project cards, architecture diagram and
repo social previews, each in a light and a dark variant.

Every glyph is converted to an SVG path at build time. GitHub serves README
SVGs under a content security policy that blocks external fonts, so live
<text> falls back to whatever font each viewer has; paths render identically
everywhere and need no font at view time.

Numbers on the cards come from ~/Desktop/New Resumes/facts.md. Change them
there first, then edit CARDS below and rebuild:

    uv run .github/design/build.py
"""
import html
import os
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "assets"))
FONTS = os.path.join(HERE, "fonts")

THEMES = {
    "dark": dict(fg="#EDEDED", mid="#A1A1A1", dim="#6B6B6B", line="#2E2E2E", grid="#1C1C1C", panel="none", solid="#0A0A0A"),
    "light": dict(fg="#171717", mid="#5E5E5E", dim="#9A9A9A", line="#E3E3E3", grid="#F0F0F0", panel="none", solid="#FFFFFF"),
}


class Face:
    def __init__(self, file):
        path = os.path.join(FONTS, file)
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet()
        self.upem = self.tt["head"].unitsPerEm
        blob = hb.Blob.from_file_path(path)
        self.hb = hb.Font(hb.Face(blob))
        self.order = self.tt.getGlyphOrder()

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        return buf.glyph_infos, buf.glyph_positions

    def width(self, text, size, track=0.0):
        _, pos = self.shape(text)
        return sum(p.x_advance for p in pos) * size / self.upem + track * max(len(pos) - 1, 0)

    def path(self, text, x, y, size, track=0.0):
        infos, pos = self.shape(text)
        s = size / self.upem
        pen = SVGPathPen(self.glyphs)
        cx = x
        for info, p in zip(infos, pos):
            name = self.order[info.codepoint]
            t = TransformPen(pen, (s, 0, 0, -s, cx + p.x_offset * s, y - p.y_offset * s))
            self.glyphs[name].draw(t)
            cx += p.x_advance * s + track
        return pen.getCommands()


SANS_SB = Face("Geist-SemiBold.ttf")
SANS_MD = Face("Geist-Medium.ttf")
SANS = Face("Geist-Regular.ttf")
MONO = Face("GeistMono-Regular.ttf")


def text(face, s, x, y, size, fill, anchor="start", track=0.0):
    w = face.width(s, size, track)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    d = face.path(s, x, y, size, track)
    return f'<path d="{d}" fill="{fill}"/>' if d else ""


def svg(w, h, body, label):
    label = html.escape(label, quote=True)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{label}">\n<title>{label}</title>\n{body}\n</svg>\n')


def dots(w, h, step, color, inset=0):
    pts = []
    y = inset + step
    while y < h - inset:
        x = inset + step
        while x < w - inset:
            pts.append(f"M{x:.0f} {y:.0f}h1.6")
            x += step
        y += step
    return f'<path d="{"".join(pts)}" stroke="{color}" stroke-width="1.6" stroke-linecap="round"/>'


def ticks(w, h, inset, size, color):
    out = []
    for cx, cy in ((inset, inset), (w - inset, inset), (inset, h - inset), (w - inset, h - inset)):
        out.append(f"M{cx - size} {cy}h{2 * size}M{cx} {cy - size}v{2 * size}")
    return f'<path d="{"".join(out)}" stroke="{color}" stroke-width="1.5"/>'


def flow(nodes, x0, y, width, t, size=24, pad=22, h=62, highlight=None):
    """A left-to-right pipeline of boxed mono labels joined by arrows."""
    widths = [MONO.width(n, size) + 2 * pad for n in nodes]
    gap = (width - sum(widths)) / max(len(nodes) - 1, 1)
    gap = max(min(gap, 64), 26)
    total = sum(widths) + gap * (len(nodes) - 1)
    x = x0 + (width - total) / 2
    out = []
    for i, (n, bw) in enumerate(zip(nodes, widths)):
        strong = highlight is not None and i == highlight
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{bw:.1f}" height="{h}" rx="10" fill="none" '
                   f'stroke="{t["fg"] if strong else t["line"]}" stroke-width="{2 if strong else 1.5}"/>')
        out.append(text(MONO, n, x + bw / 2, y + h / 2 + size * 0.36, size, t["fg"] if strong else t["mid"], "middle"))
        if i < len(nodes) - 1:
            ax, bx, ay = x + bw + 6, x + bw + gap - 6, y + h / 2
            out.append(f'<path d="M{ax:.1f} {ay}H{bx - 1:.1f}" stroke="{t["dim"]}" stroke-width="1.5"/>')
            out.append(f'<path d="M{bx - 8:.1f} {ay - 5}L{bx:.1f} {ay}L{bx - 8:.1f} {ay + 5}" fill="none" stroke="{t["dim"]}" stroke-width="1.5"/>')
        x += bw + gap
    return "\n".join(out)


CARDS = [
    dict(slug="opencodeintel", stack="Python · FastAPI · FastMCP · Pinecone · Cohere · Redis · React", idx="01", name="OpenCodeIntel", tag="MCP · RAG · EVALS",
         pitch=["Code search for AI coding agents. A web app,", "a REST API and a 12-tool MCP server."],
         flow=["repo", "tree-sitter", "BM25 + vectors", "RRF + rerank", "MCP"], hi=4,
         metrics=[("94%", "Hit@1, research eval"), ("242ms", "p50 cached, production")]),
    dict(slug="overhear", stack="TypeScript · Next.js · Retell · Claude · Postgres · Drizzle", idx="02", name="Overhear", tag="VOICE AI · LLM-AS-A-JUDGE",
         pitch=["A QA analyst for voice agents. Grades every", "call against the clinic's real database."],
         flow=["call", "Retell agent", "tool log", "code + judge", "score"], hi=3,
         metrics=[("23/23", "planted failures caught"), ("0.89", "macro-F1, 39-call set")]),
    dict(slug="callbudget", stack="Python · FastMCP · scikit-learn · Optuna · Pipecat · DuckDB", idx="03", name="CallBudget", tag="AGENTS · MCP · ML",
         pitch=["Finds a hard-to-find drug in fewer calls.", "Predicts stock, calls the likeliest first."],
         flow=["drug + area", "ranker", "call plan", "voice agent", "learn"], hi=1,
         metrics=[("4.3 → 2.3", "expected calls to find it"), ("10% → 0%", "false \"in stock\" answers")]),
    dict(slug="saar", stack="TypeScript · WXT · React · Vitest · Playwright", idx="04", name="Saar", tag="CHROME MV3 · TYPESCRIPT",
         pitch=["A Claude.ai token and cost meter that runs", "entirely in the browser. On the Chrome Web Store."],
         flow=["claude.ai", "SSE intercept", "tokenizer", "overlay"], hi=2,
         metrics=[("1,808", "Vitest tests, 63 files"), ("No backend", "data stays in browser")]),
    dict(slug="portfolio-os", stack="TypeScript · Next.js · Zustand · Framer Motion · Tailwind", idx="05", name="Portfolio OS", tag="NEXT.JS · DESIGN",
         pitch=["A desktop operating system in a browser tab.", "Window manager, terminal and dock, from scratch."],
         flow=["Next.js 15", "Zustand", "window manager", "apps"], hi=2,
         metrics=[("Next.js 15", "TypeScript, Zustand"), ("Live", "devanshuchicholikar.com")]),
    dict(slug="saar-cli", stack="Python · static analysis · PyPI · 121 commits", idx="06", name="saar CLI", tag="PYTHON · PYPI",
         pitch=["Reads a codebase and writes the files coding", "agents need: AGENTS.md, CLAUDE.md, .cursorrules."],
         flow=["repo", "static analysis", "patterns", "AGENTS.md"], hi=3,
         metrics=[("22", "releases on PyPI"), ("3", "agent context formats")]),
]


def card_body(c, t, W, H, social=False):
    m = 64
    b = []
    if social:
        b.append(f'<rect width="{W}" height="{H}" fill="{t["solid"]}"/>')
    b.append(dots(W, H, 32, t["grid"], inset=24))
    b.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="2"/>')
    b.append(ticks(W, H, 24, 7, t["dim"]))
    b.append(text(MONO, c["idx"], m, 104, 26, t["dim"]))
    b.append(text(MONO, c["tag"], W - m, 104, 25, t["dim"], "end", track=2.2))
    title_y = 230 if not social else 200
    b.append(text(SANS_SB, c["name"], m, title_y, 76, t["fg"], track=-1.6))
    for i, line in enumerate(c["pitch"]):
        b.append(text(SANS, line, m, title_y + 66 + i * 50, 38, t["mid"]))
    fy = 440 if not social else 350
    b.append(flow(c["flow"], m, fy, W - 2 * m, t, highlight=c["hi"]))
    if not social:
        b.append(text(MONO, "STACK", m, 606, 20, t["dim"], track=2.4))
        b.append(text(MONO, c["stack"], m, 646, 26, t["mid"]))
    rule_y = H - 190 if not social else H - 170
    b.append(f'<path d="M{m} {rule_y}H{W - m}" stroke="{t["line"]}" stroke-width="1.5"/>')
    col = (W - 2 * m) / 2
    for i, (big, small) in enumerate(c["metrics"]):
        x = m + i * col
        b.append(text(SANS_MD, big, x, rule_y + (88 if not social else 78), 58, t["fg"], track=-1.2))
        b.append(text(MONO, small, x, rule_y + (134 if not social else 120), 28, t["mid"]))
    return "\n".join(b)


def card_label(c):
    facts = "; ".join(f"{a} {b}" for a, b in c["metrics"])
    return f'{c["name"]}: {" ".join(c["pitch"])} Pipeline: {" to ".join(c["flow"])}. {facts}.'


def hero_body(t, W, H):
    b = [dots(W, H, 32, t["grid"], inset=8), ticks(W, H, 20, 7, t["dim"])]
    b.append(text(MONO, "DEVANSHUNEU", 40, 64, 20, t["dim"], track=3))
    b.append(text(MONO, "BOSTON, MA", W - 40, 64, 20, t["dim"], "end", track=3))
    b.append(text(SANS_SB, "Devanshu Chicholikar", W / 2, 186, 92, t["fg"], "middle", track=-2.6))
    b.append(text(MONO, "AI engineer  ·  forward deployed  ·  ships AI to production", W / 2, 246, 26, t["mid"], "middle"))
    b.append(f'<path d="M{W / 2 - 150} 286H{W / 2 + 150}" stroke="{t["line"]}" stroke-width="1.5"/>')
    meta = "MCP  ·  RAG  ·  EVALS  ·  VOICE AGENTS  ·  OPEN TO AI ENGINEER + FDE ROLES"
    mw = MONO.width(meta, 18, 2.6)
    b.append(f'<circle cx="{W / 2 - mw / 2 - 18:.1f}" cy="{330 - 6}" r="5" fill="{t["fg"]}"/>')
    b.append(text(MONO, meta, W / 2, 330, 18, t["dim"], "middle", track=2.6))
    return "\n".join(b)


def box(t, x, y, w, h, title, sub=None, strong=False):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" stroke="{t["fg"] if strong else t["line"]}" stroke-width="{2 if strong else 1.5}"/>']
    ty = y + (h / 2 + 8 if not sub else h / 2 - 6)
    out.append(text(SANS_MD, title, x + w / 2, ty, 24, t["fg"], "middle"))
    if sub:
        out.append(text(MONO, sub, x + w / 2, ty + 32, 17, t["mid"], "middle"))
    return "\n".join(out)


def arrow(t, x1, y1, x2, y2):
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 9 * math.cos(a), y2 - 9 * math.sin(a)
    px, py = 5 * math.sin(a), -5 * math.cos(a)
    return (f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{t["dim"]}" stroke-width="1.5"/>'
            f'<path d="M{hx + px:.1f} {hy + py:.1f}L{x2} {y2}L{hx - px:.1f} {hy - py:.1f}" fill="none" stroke="{t["dim"]}" stroke-width="1.5"/>')


def arch_body(t, W, H):
    b = [dots(W, H, 32, t["grid"], inset=8)]
    b.append(text(MONO, "OPENCODEINTEL  ·  ARCHITECTURE", 40, 56, 18, t["dim"], track=2.6))
    # clients
    b.append(text(MONO, "CLIENTS", 40, 120, 16, t["dim"], track=2.4))
    b.append(box(t, 40, 136, 340, 92, "Web app", "React · TypeScript"))
    b.append(box(t, 430, 136, 340, 92, "REST API", "FastAPI · 48 routes"))
    b.append(box(t, 820, 136, 340, 92, "MCP server", "FastMCP · 12 tools", strong=True))
    # the three clients share one entry into the query path
    bus = 262
    b.append(f'<path d="M210 228V{bus}M600 228V{bus}M990 228V{bus}M165 {bus}H990" stroke="{t["dim"]}" stroke-width="1.5" fill="none"/>')
    b.append(arrow(t, 165, bus, 165, 302))
    # query path
    b.append(text(MONO, "QUERY PATH", 1160, 292, 16, t["dim"], "end", track=2.4))
    q = [("embed", "OpenAI · Voyage"), ("BM25 + vectors", "Pinecone"), ("RRF fusion", "0.7 / 0.3"), ("rerank", "Cohere")]
    qx, qw, gap = 40, 250, 40
    for i, (a, s) in enumerate(q):
        x = qx + i * (qw + gap)
        b.append(box(t, x, 306, qw, 92, a, s, strong=(i == 3)))
        if i < len(q) - 1:
            b.append(arrow(t, x + qw + 4, 352, x + qw + gap - 4, 352))
    # index path
    b.append(text(MONO, "INDEX PATH", 40, 460, 16, t["dim"], track=2.4))
    ix = [("repo", "GitHub"), ("tree-sitter", "function AST chunks"), ("embeddings", "signature + docstring"), ("index", "Pinecone · BM25")]
    for i, (a, s) in enumerate(ix):
        x = qx + i * (qw + gap)
        b.append(box(t, x, 474, qw, 92, a, s))
        if i < len(ix) - 1:
            b.append(arrow(t, x + qw + 4, 520, x + qw + gap - 4, 520))
    # stores
    b.append(text(MONO, "STATE", 40, 628, 16, t["dim"], track=2.4))
    b.append(box(t, 40, 642, 540, 80, "Supabase Postgres", "auth · repos · row-level security"))
    b.append(box(t, 620, 642, 540, 80, "Redis", "result cache · indexing progress pub/sub"))
    return "\n".join(b)


def write(name, content):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(content)


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, "social"), exist_ok=True)
    for theme, t in THEMES.items():
        write(f"hero-{theme}.svg", svg(1200, 380, hero_body(t, 1200, 380),
              "Devanshu Chicholikar. AI engineer and forward deployed engineer in Boston who ships AI to production: MCP, RAG, evals, voice agents. Open to AI Engineer and FDE roles."))
        for c in CARDS:
            write(f"card-{c['slug']}-{theme}.svg", svg(1200, 900, card_body(c, t, 1200, 900), card_label(c)))
        write(f"oci-architecture-{theme}.svg", svg(1200, 760, arch_body(t, 1200, 760),
              "OpenCodeIntel architecture: web app, REST API and MCP server clients; query path embed, BM25 plus vectors, RRF fusion, Cohere rerank; index path tree-sitter chunks, embeddings, Pinecone and BM25; state in Supabase Postgres and Redis."))
    for c in CARDS:
        write(f"social/{c['slug']}.svg", svg(1280, 640, card_body(c, THEMES["dark"], 1280, 640, social=True), card_label(c)))
    print("built into", OUT)


if __name__ == "__main__":
    main()
