"""ReportLab PDF generation for validated WellNote research documents."""

from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

import research_decoder


INK = colors.HexColor("#22372c")
GREEN = colors.HexColor("#365d49")
MUTED = colors.HexColor("#65746a")
PALE = colors.HexColor("#edf1e9")
LINE = colors.HexColor("#dce4da")
PAPER = colors.white


def _paragraph_text(value):
    return escape(str(value)).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br/>")


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "WellNoteTitle", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=22, leading=27, textColor=INK, spaceAfter=8, alignment=TA_LEFT,
        ),
        "subtitle": ParagraphStyle(
            "WellNoteSubtitle", parent=base["Normal"], fontName="Helvetica",
            fontSize=9, leading=14, textColor=MUTED, spaceAfter=12,
        ),
        "section": ParagraphStyle(
            "WellNoteSection", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=13, leading=17, textColor=GREEN, spaceBefore=10, spaceAfter=7,
            keepWithNext=True,
        ),
        "subhead": ParagraphStyle(
            "WellNoteSubhead", parent=base["Heading3"], fontName="Helvetica-Bold",
            fontSize=9, leading=12, textColor=GREEN, spaceBefore=4, spaceAfter=4,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "WellNoteBody", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9, leading=14, textColor=INK, spaceAfter=7, splitLongWords=True,
        ),
        "small": ParagraphStyle(
            "WellNoteSmall", parent=base["BodyText"], fontName="Helvetica",
            fontSize=8, leading=12, textColor=MUTED, spaceAfter=5, splitLongWords=True,
        ),
        "table_header": ParagraphStyle(
            "WellNoteTableHeader", parent=base["BodyText"], fontName="Helvetica-Bold",
            fontSize=8, leading=11, textColor=INK,
        ),
        "table_cell": ParagraphStyle(
            "WellNoteTableCell", parent=base["BodyText"], fontName="Helvetica",
            fontSize=7.5, leading=11, textColor=INK, splitLongWords=True,
        ),
    }


def _page_chrome(canvas, document):
    canvas.saveState()
    width, height = letter
    canvas.setFillColor(PALE)
    canvas.rect(0, height - 0.62 * inch, width, 0.62 * inch, fill=1, stroke=0)
    canvas.setFillColor(GREEN)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(document.leftMargin, height - 0.39 * inch, "WELLNOTE  /  RESEARCH DECODER")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(document.leftMargin, 0.55 * inch, width - document.rightMargin, 0.55 * inch)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(
        document.leftMargin, 0.36 * inch,
        "Educational study aid · Not medical advice · Verify against the full paper",
    )
    canvas.drawRightString(width - document.rightMargin, 0.36 * inch, f"Page {document.page}")
    canvas.restoreState()


def _table(headers, rows, fields, column_widths, styles):
    table_data = [[
        Paragraph(_paragraph_text(header), styles["table_header"])
        for header in headers
    ]]
    for row in rows:
        table_data.append([
            Paragraph(_paragraph_text(row[field]), styles["table_cell"])
            for field in fields
        ])
    result = Table(
        table_data,
        colWidths=column_widths,
        repeatRows=1,
        splitByRow=1,
        hAlign="LEFT",
    )
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("TEXTCOLOR", (0, 0), (-1, 0), INK),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PAPER, colors.HexColor("#fbfcf9")]),
    ]))
    return result


def _key_takeaways(sections):
    content = {section["title"]: section["content"] for section in sections}
    objective = content["Objective"]
    method = content["Study design and methodology"]
    results = content["Important results and statistics"]
    conclusion = content["Conclusion"]["simplified_interpretation"]
    limitations = content["Limitations of the study"]
    main_result = (
        f'{results[0]["finding"]} ({results[0]["reported_value"]})'
        if results else "The abstract reports no numerical results."
    )
    caveat = limitations["potentially_inferred"] or limitations["not_reported_in_abstract"]
    return [
        ("Research question", objective),
        ("Main reported result", main_result),
        ("Study context", method),
        ("Plain-language interpretation", conclusion),
        ("Keep in mind", caveat),
    ]


def _build_story(document, styles):
    paper = document["paper"]
    sections = document["sections"]
    story = [
        Paragraph("Research Decoder", styles["subtitle"]),
        Paragraph(_paragraph_text(paper["title"] or "Research abstract study aid"), styles["title"]),
        Paragraph(
            "A learning document based only on the abstract pasted into WellNote. "
            "The complete research paper has not been analyzed.",
            styles["subtitle"],
        ),
        Paragraph("Original abstract", styles["section"]),
        Paragraph(_paragraph_text(paper["abstract"]), styles["body"]),
        Spacer(1, 4),
        Paragraph("Key takeaways", styles["section"]),
    ]
    for label, value in _key_takeaways(sections):
        story.append(Paragraph(f"<b>{_paragraph_text(label)}:</b> {_paragraph_text(value)}", styles["body"]))

    content = {section["title"]: section["content"] for section in sections}
    for index, section in enumerate(sections, 1):
        story.append(Paragraph(
            f"{index}. {_paragraph_text(section['title'])}",
            styles["section"],
        ))
        value = section["content"]
        if section["title"] == "Important results and statistics":
            if value:
                story.append(_table(
                    ("Finding", "Reported value", "Interpretation"),
                    value,
                    research_decoder.RESULT_FIELDS,
                    (1.35 * inch, 1.15 * inch, 4.0 * inch),
                    styles,
                ))
            else:
                story.append(Paragraph("No numerical results were reported in the abstract.", styles["body"]))
        elif section["title"] == "Difficult terminology explained":
            if value:
                story.append(_table(
                    ("Medical term", "Simple meaning", "Relevance to this study"),
                    value,
                    research_decoder.TERM_FIELDS,
                    (1.3 * inch, 2.25 * inch, 2.95 * inch),
                    styles,
                ))
            else:
                story.append(Paragraph("No difficult medical terms were identified in the abstract.", styles["body"]))
        elif section["title"] == "Conclusion":
            story.extend([
                Paragraph("Authors' conclusion", styles["subhead"]),
                Paragraph(_paragraph_text(value["authors_conclusion"]), styles["body"]),
                Paragraph("Simplified interpretation", styles["subhead"]),
                Paragraph(_paragraph_text(value["simplified_interpretation"]), styles["body"]),
            ])
        elif section["title"] == "Limitations of the study":
            for label, key in (
                ("Stated by the authors", "stated_by_authors"),
                ("Potentially inferred concerns", "potentially_inferred"),
                ("Not reported in the abstract", "not_reported_in_abstract"),
            ):
                story.extend([
                    Paragraph(label, styles["subhead"]),
                    Paragraph(_paragraph_text(value[key]), styles["body"]),
                ])
        else:
            story.append(Paragraph(_paragraph_text(value), styles["body"]))

    story.extend([
        Spacer(1, 8),
        Paragraph(
            "Educational disclaimer",
            styles["section"],
        ),
        Paragraph(
            "This document explains an abstract for study purposes only. It is not "
            "medical advice, does not support individual diagnosis or treatment "
            "decisions, and may contain errors. Abstracts can omit important "
            "methods and context. Verify the interpretation against the full paper "
            "and current evidence.",
            styles["small"],
        ),
    ])
    return story


def generate_pdf(document):
    """Render the validated abstract and all nine sections as a paginated PDF."""
    if not isinstance(document, dict) or set(document) != {"paper", "sections"}:
        raise ValueError("A validated research document is required.")
    paper = research_decoder._paper_data(document["paper"])
    section_map = {
        section.get("title"): section.get("content")
        for section in document["sections"]
        if isinstance(section, dict)
    } if isinstance(document["sections"], list) else None
    sections, error = research_decoder.validate_sections(section_map)
    if error or not paper["abstract"]:
        raise ValueError(error or "The original abstract is missing.")
    output = BytesIO()
    page_width, page_height = letter
    left = right = 0.75 * inch
    top = 0.82 * inch
    bottom = 0.74 * inch
    doc = BaseDocTemplate(
        output,
        pagesize=letter,
        leftMargin=left,
        rightMargin=right,
        topMargin=top,
        bottomMargin=bottom,
        title=paper["title"] or "WellNote Research Decoder",
        author="WellNote",
        subject="Educational explanation of a medical research abstract",
        allowSplitting=1,
    )
    frame = Frame(
        left, bottom, page_width - left - right, page_height - top - bottom,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id="wellnote-content",
    )
    doc.addPageTemplates([
        PageTemplate(id="wellnote-pages", frames=[frame], onPage=_page_chrome)
    ])
    doc.build(_build_story(
        {"paper": paper, "sections": sections},
        _styles(),
    ))
    return output.getvalue()
