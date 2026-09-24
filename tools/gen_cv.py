#!/usr/bin/env python3
"""Regenerate assets/files/curriculum_vitae.pdf from scratch.

Fonts are vendored in tools/fonts/ (NanumGothic, SIL OFL) so this has no
network dependency and won't disappear when a temp/scratch dir gets wiped.

HOW TO ADD A NEW ENTRY
-----------------------
LINES is a flat list of draw calls, top to bottom, in the exact order they
appear on the page. Each line is (x, y, text, font, size). Copy the pattern
of the section/entry you're extending and adjust y using these measured
deltas (all in points, y decreases going down the page):

  HEADER_TO_RULE       = 3.1   section header baseline -> its underline
  HEADER_TO_CONTENT    = 20.0  section header baseline -> first entry line
  LINE_STEP            = 19.1  same-style line -> next same-style line
                                (INTERESTS/HONORS bullets, wrapped bold titles)
  LINE_TO_ITALIC       = 15.2  bold/plain line -> italic subtitle right after
                                (also italic -> italic, e.g. authors -> venue)
  SECTION_GAP          = 31.6  last line of a section -> next section's rule

Left margin x=41.4 (dash bullets, section headers, HONORS lines).
Hanging indent x=59.4 (entry titles/subtitles that follow a dash).
Right margin x=558.9 (right-aligned location/date text ends here).
Rule spans x=36.0 to x=558.9, width 0.5.
Section header: first letter at size 11, rest of the word at size 9,
baseline of the size-9 part is +0.4 above the size-11 part.

After editing LINES, run:  python3 tools/gen_cv.py
"""
import os

from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "assets", "files", "curriculum_vitae.pdf")
PAGE_W, PAGE_H = 595.32, 841.92
LEFT, INDENT, RIGHT, RULE_X0 = 41.4, 59.4, 558.9, 36.0

pdfmetrics.registerFont(TTFont("NanumGothic", os.path.join(HERE, "fonts", "NanumGothic-Regular.ttf")))
pdfmetrics.registerFont(TTFont("NanumGothicBold", os.path.join(HERE, "fonts", "NanumGothicBold.ttf")))
REG, BOLD, ITALIC = "NanumGothic", "NanumGothicBold", "Times-Italic"
SKY = (0.058824, 0.619608, 0.835294)  # name color from the original CV (#0F9ED5)

# Each entry: (x, y_baseline, text, font, size) drawn left-aligned,
# or ("R", right_x, y_baseline, text, font, size) drawn right-aligned.
LINES = [
    # --- header ---
    (LEFT, 786.52, "Jiyong Choi", BOLD, 13.5, SKY),
    ("R", RIGHT, 786.52, "Email: yongyong@hansung.ac.kr", REG, 11),
    (LEFT, 768.12, "Undergraduate Student, Dept. Applied AI", REG, 11),
    ("R", RIGHT, 768.12, "Mobile: +82-10-5787-4580", REG, 11),
    (LEFT, 748.62, "B.S. Student @ Hansung Univ.", REG, 11),
    ("R", RIGHT, 748.62, "116 Samseongyoro, Seongbuk-gu, Seoul, Rep. Korea", REG, 11),

    # --- INTERESTS ---
    (LEFT, 709.02, "I", REG, 11), (44.1, 709.42, "NTERESTS", REG, 9),
    ("RULE", 705.92),
    (LEFT, 689.02, "-", REG, 11), (INDENT, 689.02, "Generative AI", REG, 11),
    (LEFT, 669.92, "-", REG, 11), (INDENT, 669.92, "Computer Vision", REG, 11),

    # --- EXPERIENCE ---
    (LEFT, 641.32, "E", REG, 11), (47.7, 641.72, "XPERIENCE", REG, 9),
    ("RULE", 638.22),
    (LEFT, 621.32, "-", REG, 11), (INDENT, 621.32, "Visual Intelligence Lab.", BOLD, 11),
    ("R", RIGHT, 621.32, "Seoul, Rep. Korea", REG, 11),
    (INDENT, 606.13, "Undergraduate Intern, Advisor: Heeseok Oh", ITALIC, 11),

    # --- EDUCATION ---
    (LEFT, 577.72, "E", REG, 11), (47.7, 578.12, "DUCATION", REG, 9),
    ("RULE", 574.62),
    (LEFT, 557.72, "-", REG, 11), (INDENT, 557.72, "Hansung University", BOLD, 11),
    ("R", RIGHT, 557.72, "Seoul, Rep. Korea", REG, 11),
    (INDENT, 542.53, "B.S. in Applied AI.", ITALIC, 11),
    ("R", RIGHT, 542.53, "Mar. 2023 – Present", ITALIC, 11),

    # --- HONORS ---
    (LEFT, 514.12, "H", REG, 11), (49.4, 514.52, "ONORS", REG, 9),
    ("RULE", 511.02),
    (LEFT, 494.12, "-", REG, 11), (INDENT, 494.12, "3rd Place, Landslide Scar Detection, 2026 National Park AI Challenge, AIFactory, 2026", REG, 11),
    (LEFT, 475.02, "-", REG, 11), (INDENT, 475.02, "3rd Place, Dead Conifer Detection, 2026 National Park AI Challenge, AIFactory, 2026", REG, 11),
    (LEFT, 455.92, "-", REG, 11), (INDENT, 455.92, "3rd Place (3/1,087), LG Aimers 9th Online Hackathon, DACON, 2026", REG, 11),
    (LEFT, 436.82, "-", REG, 11), (INDENT, 436.82, "Top 7%, AI Agent Behavior Inference Challenge, DACON, 2026", REG, 11),

    # --- PROJECTS ---
    (LEFT, 408.22, "P", REG, 11), (47.7, 408.62, "ROJECTS", REG, 9),
    ("RULE", 405.12),
    (LEFT, 388.22, "-", REG, 11),
    (INDENT, 388.22, "A Study on the Reasoning Emergence and Test-Time Scaling in Small Vision-Language Model", BOLD, 11),
    (INDENT, 369.12, "Comprehension and Generation via Reinforcement Learning with Perceptual Reward", BOLD, 11),
    (INDENT, 353.93, "NRF, 2026-2028", ITALIC, 11),
    (LEFT, 333.25, "-", REG, 11),
    (INDENT, 333.25, "Multi-Pipeline 3D Reconstruction and Scan-to-CAD Registration System (Team SCRS)", BOLD, 11),
    (INDENT, 317.24, "Hansung Univ.·KIST AI·SW Industry-Academic Collaboration Project, Apr.–Jul. 2026", ITALIC, 11),

    # --- PUBLICATIONS ---
    (LEFT, 289.55, "P", REG, 11), (47.7, 290.23, "UBLICATIONS", REG, 9),
    ("RULE", 288.03),
    (LEFT, 269.55, "-", REG, 11),
    (INDENT, 269.55, "An Integrated Scan-to-CAD Pipeline for RGB Image-Based S²-2DGS 3D Reconstruction", BOLD, 11),
    (INDENT, 250.45, "and CAD Registration", BOLD, 11),
    (INDENT, 234.44, "S. Seo, J. Park, J. Choi, and H. Oh (Corr.)", ITALIC, 11),
    (INDENT, 219.24, "IEIE, Submitted, 2026", ITALIC, 11),

    # --- ADD NEW ENTRIES ABOVE THIS LINE, using the deltas documented up top ---
]


def build():
    c = canvas.Canvas(OUT_PATH, pagesize=(PAGE_W, PAGE_H))
    c.setLineWidth(0.5)
    c.setStrokeColor(black)
    for item in LINES:
        if item[0] == "RULE":
            c.line(RULE_X0, item[1], RIGHT, item[1])
        elif item[0] == "R":
            _, right_x, y, text, font, size = item
            w = pdfmetrics.stringWidth(text, font, size)
            c.setFont(font, size)
            c.drawString(right_x - w, y, text)
        else:
            x, y, text, font, size = item[:5]
            c.setFillColorRGB(*(item[5] if len(item) > 5 else (0, 0, 0)))
            c.setFont(font, size)
            c.drawString(x, y, text)
            c.setFillColorRGB(0, 0, 0)
    c.save()

    r = PdfReader(OUT_PATH)
    w = PdfWriter()
    w.add_page(r.pages[0])
    w.add_metadata({"/Title": "Jiyong Choi - Curriculum Vitae", "/Author": "Jiyong Choi"})
    with open(OUT_PATH, "wb") as f:
        w.write(f)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    build()
