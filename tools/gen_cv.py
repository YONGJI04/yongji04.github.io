#!/usr/bin/env python3
"""Regenerate assets/files/curriculum_vitae.pdf from scratch.

Fonts are vendored in tools/fonts/ (NanumGothic, SIL OFL), so there is no
network dependency. To change the CV, edit the CONTENT block in build()
(sections and entries, top to bottom) and run:

    python3 tools/gen_cv.py [output.pdf]

Layout is cursor based: every helper draws at the current y and moves it down.
"""
import os
import sys

from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "..", "assets", "files", "curriculum_vitae.pdf")
PAGE_W, PAGE_H = 595.32, 841.92
LEFT, INDENT, RIGHT = 41.4, 59.4, 558.9

pdfmetrics.registerFont(TTFont("NanumGothic", os.path.join(HERE, "fonts", "NanumGothic-Regular.ttf")))
pdfmetrics.registerFont(TTFont("NanumGothicBold", os.path.join(HERE, "fonts", "NanumGothicBold.ttf")))
REG, BOLD, ITALIC = "NanumGothic", "NanumGothicBold", "Times-Italic"

SKY = (0.058824, 0.619608, 0.835294)  # #0F9ED5, the name color of the original CV
INK = (0, 0, 0)
GREY = (0.35, 0.35, 0.35)
NAVY = (0.016, 0.200, 0.380)  # #043361, the heading color of the main site
RULE = (0.35, 0.35, 0.35)  # section underline

BODY = 11.5          # body font size; everything below scales with it
K = BODY / 11.0
TITLE_SIZE = 15.5
LINE_STEP = 19.1 * K     # line -> next line of the same style
TO_SUB = 15.2 * K        # title line -> its italic sub line
ENTRY_GAP = 24.0 * K     # last line of an entry -> title of the next entry
SECTION_GAP = 44.0 * K   # last line of a section -> next section title baseline
TITLE_TO_RULE = 5.5
RULE_TO_ENTRY = 24.0 * K


class CV:
    def __init__(self, out):
        self.out = out
        self.c = canvas.Canvas(out, pagesize=(PAGE_W, PAGE_H))
        self.y = PAGE_H - 52
        self.L, self.I, self.R = LEFT, INDENT, RIGHT  # column-local left / indent / right edges
        self.gap = None  # distance already spent below the previous section's last line

    def text(self, x, s, font=REG, size=BODY, color=INK, right=False):
        w = pdfmetrics.stringWidth(s, font, size)
        self.c.setFillColorRGB(*color)
        self.c.setFont(font, size)
        self.c.drawString(self.R - w if right else x, self.y, s)
        return w

    def header(self, name, role, email, mobile, address):
        self.text(LEFT, name, BOLD, 20, SKY)
        self.text(0, email, REG, BODY - 1, GREY, right=True)
        self.y -= 24 * K
        self.text(LEFT, role)
        self.text(0, mobile, REG, BODY - 1, GREY, right=True)
        self.y -= 20 * K
        self.text(LEFT, address, REG, BODY - 1, GREY)
        self.y -= 40 * K

    def section(self, title):
        if self.gap is not None:
            self.y -= SECTION_GAP - self.gap
        self.text(self.L, title, BOLD, TITLE_SIZE, NAVY)
        self.y -= TITLE_TO_RULE
        self.c.setStrokeColorRGB(*RULE)
        self.c.setLineWidth(0.5)
        self.c.line(self.L - 5.4, self.y, self.R, self.y)
        self.y -= RULE_TO_ENTRY

    def award(self, rank, rest):
        self.text(self.L, "-")
        w = self.text(self.I, rank, BOLD)
        self.text(self.I + w, rest)
        self.y -= LINE_STEP
        self.gap = LINE_STEP

    def entry(self, title_lines, sub=None, sub2=None, right=None, right_sub=None):
        self.text(self.L, "-")
        title_lines = [w for t in title_lines for w in self.wrap(t)]
        for i, line in enumerate(title_lines):
            self.text(self.I, line, BOLD)
            if i == 0 and right:
                self.text(0, right, REG, right=True)
            if i < len(title_lines) - 1:
                self.y -= LINE_STEP
        if sub:
            self.y -= TO_SUB
            self.text(self.I, sub, ITALIC)
            if right_sub:
                self.text(0, right_sub, ITALIC, right=True)
        if sub2:
            self.y -= TO_SUB
            self.text(self.I, sub2, ITALIC)
        self.y -= ENTRY_GAP
        self.gap = ENTRY_GAP

    def wrap(self, s):
        """Word wrap a bold title to the column width, balancing line lengths (no one-word last line)."""
        def greedy(limit):
            lines, cur = [], ""
            for word in s.split():
                trial = (cur + " " + word).strip()
                if cur and pdfmetrics.stringWidth(trial, BOLD, BODY) > limit:
                    lines.append(cur)
                    cur = word
                else:
                    cur = trial
            return lines + [cur]
        limit = self.R - self.I - 4
        n = len(greedy(limit))
        lo, hi = limit / 2, limit
        for _ in range(20):
            mid = (lo + hi) / 2
            if len(greedy(mid)) <= n:
                hi = mid
            else:
                lo = mid
        return greedy(hi)

    def bullet(self, s):
        self.text(self.L, "-")
        self.text(self.I, s)
        self.y -= LINE_STEP
        self.gap = LINE_STEP

    def columns(self, left, right, ratio=0.3, gutter=22.0):
        """Run two section builders side by side; the cursor ends below the taller one."""
        split = LEFT + ratio * (RIGHT - LEFT)
        top, ends = self.y, []
        for build_col, (l, i, r) in ((left, (LEFT, INDENT, split)),
                                      (right, (split + gutter, split + gutter + 18, RIGHT))):
            self.y, self.gap = top, None
            self.L, self.I, self.R = l, i, r
            build_col(self)
            ends.append((self.y, self.gap))
        self.L, self.I, self.R = LEFT, INDENT, RIGHT
        self.y, self.gap = min(ends, key=lambda e: e[0])
        self.gap -= 10  # extra breathing room below the top two-column row

    def save(self):
        self.c.save()
        r = PdfReader(self.out)
        w = PdfWriter()
        w.add_page(r.pages[0])
        w.add_metadata({"/Title": "Jiyong Choi - Curriculum Vitae", "/Author": "Jiyong Choi"})
        with open(self.out, "wb") as f:
            w.write(f)


def build(out=DEFAULT_OUT):
    cv = CV(out)

    # ---------------- CONTENT: edit below ----------------
    cv.header(
        name="Jiyong Choi",
        role="Undergraduate Student, Dept. of Applied AI, Hansung University",
        email="yongyong@hansung.ac.kr",
        mobile="+82-10-5787-4580",
        address="116 Samseongyoro, Seongbuk-gu, Seoul",
    )

    def interests(c):
        c.section("Interests")
        c.bullet("Generative AI")
        c.bullet("Computer Vision")

    def experience(c):
        c.section("Experience")
        c.entry(["Visual Intelligence Lab."], sub="Undergraduate Intern, Advisor: Heeseok Oh")

    cv.columns(interests, experience, ratio=0.3)

    cv.section("Honors & Awards")
    cv.award("3rd Place", ", Landslide Scar Detection, 2026 National Park AI Challenge, AIFactory, 2026")
    cv.award("3rd Place", ", Dead Conifer Detection, 2026 National Park AI Challenge, AIFactory, 2026")
    cv.award("3rd Place", " (3/1,087), LG Aimers 9th Online Hackathon, DACON, 2026")
    cv.award("Top 7%", ", AI Agent Behavior Inference Challenge, DACON, 2026")

    cv.section("Publications")
    cv.entry(
        ["An Integrated Scan-to-CAD Pipeline for RGB Image-Based S²-2DGS 3D Reconstruction and CAD Registration"],
        sub="S. Seo, J. Park, J. Choi, and H. Oh (Corr.)",
        sub2="IEIE, Submitted, 2026",
    )

    cv.section("Projects")
    cv.entry(
        ["A Study on the Reasoning Emergence and Test-Time Scaling in Small Vision-Language Model Comprehension and Generation via Reinforcement Learning with Perceptual Reward"],
        sub="NRF, 2026-2028",
    )
    cv.entry(
        ["Multi-Pipeline 3D Reconstruction and Scan-to-CAD Registration System (Team SCRS)"],
        sub="Hansung Univ.·KIST AI·SW Industry-Academic Collaboration Project, Apr.–Jul. 2026",
    )
    cv.entry(
        ["Industry Collaboration Project"],
        sub="LemonCloud, Sep. 2026 – Present",
    )
    # ---------------- CONTENT: end ----------------

    cv.save()


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    build(out)
    print("wrote", out)
