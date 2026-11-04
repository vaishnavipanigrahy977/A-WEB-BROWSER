"""Escaped HTML rendering for the Python-only server-rendered app."""

from html import escape
import re
from urllib.parse import quote


def e(value):
    return escape(str(value), quote=True)


def layout(title, content, active="home"):
    links = [("home", "/", "Explore"), ("study", "/study", "Study room"), ("saved", "/saved", "Saved")]
    nav = "".join(
        f'<a class="nav-link{" active" if key == active else ""}" href="{href}">{label}</a>'
        for key, href, label in links
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f5f6ef"><title>{e(title)} · Wellnote</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet"><link rel="stylesheet" href="/static/style.css"></head><body><header class="site-header"><a class="brand" href="/"><span class="brand-mark">w</span><span>wellnote<span class="brand-period">.</span></span></a><nav class="main-nav" aria-label="Main navigation">{nav}</nav><span class="header-note"><span class="status-dot"></span>A calmer way to learn</span></header><main>{content}</main><footer class="site-footer"><a class="brand footer-brand" href="/"><span class="brand-mark">w</span><span>wellnote<span class="brand-period">.</span></span></a><p>Clearer health learning, one topic at a time.</p><p class="footer-disclaimer">For education only · Not a substitute for professional medical advice</p></footer></body></html>"""


def disease_card(disease, saved=False):
    slug = quote(disease["slug"], safe="")
    action = "remove" if saved else "add"
    icon = "♥" if saved else "＋"
    return f"""<article class="disease-card"><div class="card-topline"><span class="category-label">{e(disease["category"])}</span><form action="/saved/{action}/{slug}" method="post"><button class="save-button" type="submit" aria-label="{'Remove from' if saved else 'Save to'} library: {e(disease['name'])}">{icon}</button></form></div><a class="card-main" href="/disease/{slug}"><h3>{e(disease["name"])}</h3><p>{e(disease["summary"])}</p><span class="text-link">Explore topic <span>↗</span></span></a></article>"""


def reference_results(query, results, error=None):
    if not results:
        detail = (
            f'<p>{e(error)}</p>' if error else
            "<p>MedlinePlus did not find a matching health topic. Try a broader search directly on the MedlinePlus website.</p>"
        )
        return f"""<section class="content-panel external-fallback"><span class="source-icon">↗</span><div><span class="eyebrow">MEDLINEPLUS REFERENCE</span><h3>No reviewed Wellnote guide for “{e(query)}”</h3>{detail}<p>We won’t guess at symptoms or treatment. MedlinePlus is the U.S. National Library of Medicine’s health information service.</p><a class="button button-dark" href="https://medlineplus.gov/" target="_blank" rel="noopener noreferrer">Visit MedlinePlus ↗</a></div></section>"""
    items = "".join(
        f'<article class="content-panel reference-result"><span class="eyebrow">MEDLINEPLUS · NATIONAL LIBRARY OF MEDICINE</span><h3>{e(item["title"])}</h3><p>{e(item["summary"])}</p><a class="text-link" href="{e(item["url"])}" target="_blank" rel="noopener noreferrer">Read the full reference ↗</a></article>'
        for item in results
    )
    return f'<div class="reference-results"><section class="content-panel reference-intro"><span class="eyebrow">TRUSTED HEALTH REFERENCES</span><h3>Information for “{e(query)}”</h3><p>These summaries are provided by MedlinePlus, a service of the U.S. National Library of Medicine. Open a source for its full article and references.</p></section>{items}</div>'


def home_page(diseases, query="", external_results=None, external_error=None):
    cards = "".join(disease_card(item) for item in diseases)
    count_label = (
        f'{len(external_results)} references'
        if query and external_results
        else "External lookup"
        if query and not diseases
        else f"{len(diseases)} topics"
    )
    if not cards:
        cards = reference_results(query, external_results or [], external_error)
    search = e(query)
    content = f"""<section class="hero"><div class="hero-copy"><span class="eyebrow"><span class="sparkle">✳</span>YOUR PERSONAL HEALTH LIBRARY</span><h1>Understand health.<br><span>Feel more prepared.</span></h1><p class="hero-description">Clear, thoughtful guides to health topics—made for learning, not self-diagnosis.</p><form class="search-form" action="/" method="get" role="search"><label class="sr-only" for="disease-search">Search health topics</label><span class="search-icon">⌕</span><input id="disease-search" type="search" name="q" value="{search}" placeholder="Search a disease or condition"><button type="submit">Search <span>→</span></button></form><p class="search-hint">Try “asthma”, “diabetes”, or “flu”</p></div><div class="hero-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="hero-sun"></div><div class="hero-leaf leaf-one"></div><div class="hero-leaf leaf-two"></div><div class="hero-note"><span class="note-icon">✳</span><span><strong>Knowledge is care</strong><small>Learn at your own pace</small></span></div><div class="hero-caption">A little more clarity,<br>a little less overwhelm.</div></div></section><section class="library-section"><div class="section-heading"><div><span class="eyebrow">THE LIBRARY</span><h2>{'Search results' if query else 'Explore health topics'}</h2><p>{f'Results for “{search}”' if query else 'Start with a topic, follow your curiosity.'}</p></div><span class="count-pill">{count_label}</span></div><div class="card-grid">{cards}</div></section><section class="study-banner"><div class="study-symbol">✎</div><div><span class="eyebrow">MAKE IT STICK</span><h2>Curiosity, meet your study room.</h2><p>Review health topics, ask the study buddy, and practice original questions.</p></div><a class="button button-dark" href="/study">Visit study room <span>→</span></a></section>{notice('A note on health information', 'These guides are educational, not medical advice. They cover a small set of common topics, not every disease. Always talk with a qualified health professional about personal symptoms or care.')}"""
    return layout("Explore health topics", content)


def external_topic_page(topic, results=None, error=None):
    """Render linked NLM references or a clear fallback without inventing facts."""
    content = f"""<section class="simple-hero"><a class="back-link" href="/">← All topics</a><span class="eyebrow">EXTERNAL HEALTH REFERENCE</span><h1>{e(topic)}<span class="brand-period">.</span></h1><p>This condition is not in Wellnote’s small, reviewed starter library.</p></section>{reference_results(topic, results or [], error)}{notice('For education, not diagnosis.', 'Online references cannot assess your personal health. For symptoms or care, talk with a qualified health professional; for a possible emergency, contact local emergency services.')}"""
    return layout(f"Find information about {topic}", content)


def notice(title, text):
    return f'<aside class="notice"><span class="notice-icon">i</span><p><strong>{e(title)}</strong><br>{e(text)}</p></aside>'


def study_response_html(response):
    lines = response.splitlines()
    rendered = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if (
            line.startswith("|")
            and index + 1 < len(lines)
            and re.fullmatch(r"\|?[\s:|-]+\|?", lines[index + 1])
        ):
            headers = [cell.strip() for cell in line.strip("|").split("|")]
            index += 2
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                rows.append([cell.strip() for cell in lines[index].strip("|").split("|")])
                index += 1
            head = "".join(f"<th>{e(cell)}</th>" for cell in headers)
            body = "".join(
                "<tr>" + "".join(f"<td>{e(cell)}</td>" for cell in row) + "</tr>"
                for row in rows
            )
            rendered.append(f'<div class="response-table-wrap"><table class="response-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
            continue
        if line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            rendered.append('<p class="response-table-line">' + " · ".join(e(cell) for cell in cells) + "</p>")
        elif line.startswith("LINK:") and "|" in line:
            label, url = line[5:].split("|", 1)
            rendered.append(
                f'<a class="text-link" href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)} ↗</a>'
            )
        elif line:
            rendered.append(f"<p>{e(line)}</p>")
        index += 1
    return "".join(rendered)


def disease_page(disease, saved=False):
    bullets = lambda values: "".join(f"<li>{e(value)}</li>" for value in values)
    action = "remove" if saved else "add"
    save_label = "♥ Saved to your library" if saved else "＋ Save for later"
    points = bullets(disease["study_points"])
    content = f"""<section class="detail-hero"><a class="back-link" href="/">← All topics</a><span class="eyebrow">{e(disease["category"])}</span><div class="detail-title-row"><div><h1>{e(disease["name"])}</h1><p class="detail-summary">{e(disease["summary"])}</p></div><form action="/saved/{action}/{quote(disease['slug'], safe='')}" method="post"><button class="button button-save">{save_label}</button></form></div></section><div class="detail-layout"><article class="detail-article"><section class="content-panel"><span class="eyebrow">THE OVERVIEW</span><h2>What it is</h2><p>{e(disease["description"])}</p></section><section class="content-panel"><div class="panel-heading"><span class="panel-icon icon-coral">✳</span><div><span class="eyebrow">WHAT TO LOOK FOR</span><h2>Common symptoms</h2></div></div><ul class="check-list">{bullets(disease["symptoms"])}</ul><p class="quiet-note">Symptoms can vary. This list cannot tell you what is causing your symptoms.</p></section><section class="content-panel"><div class="panel-heading"><span class="panel-icon icon-green">↗</span><div><span class="eyebrow">EVERYDAY WELLBEING</span><h2>Prevention &amp; risk reduction</h2></div></div><ul class="check-list">{bullets(disease["prevention"])}</ul></section><section class="content-panel treatment-panel"><div class="panel-heading"><span class="panel-icon icon-blue">✚</span><div><span class="eyebrow">CARE &amp; TREATMENT</span><h2>Can it be treated?</h2></div></div><p>{e(disease["treatment"])}</p><div class="care-callout"><span>♡</span><p>Care is personal. A licensed health professional can help you understand your options and what is right for you.</p></div></section><section class="source-panel"><span class="source-icon">↗</span><p>Learn more from <a href="{e(disease['source_url'])}" target="_blank" rel="noopener noreferrer">{e(disease["source_name"])} ↗</a></p></section></article><aside class="study-sidebar"><div class="sidebar-card"><span class="eyebrow">QUICK REVIEW</span><h3>Key takeaways</h3><ul>{points}</ul><a class="text-link" href="/study/{quote(disease['slug'], safe='')}">Study this topic →</a></div><div class="urgent-card"><span class="urgent-icon">!</span><p><strong>Need medical help?</strong><br>If you think you may have a medical emergency, contact your local emergency services now.</p></div></aside></div>{notice('Learning, not diagnosis.', 'This overview is general education and is not a substitute for a clinician’s assessment, diagnosis, or treatment advice.')}"""
    return layout(disease["name"], content)


def saved_page(diseases):
    cards = "".join(disease_card(item, saved=True) for item in diseases)
    if not cards:
        cards = '<div class="empty-state"><span class="empty-icon">♡</span><h3>Your library is ready</h3><p>Save a health topic to keep it close for your next study session.</p><a class="button button-outline" href="/">Explore health topics</a></div>'
    content = f'<section class="simple-hero"><span class="eyebrow">YOUR PERSONAL LIBRARY</span><h1>Saved topics<span class="brand-period">.</span></h1><p>Pick up where your curiosity left off.</p></section><section class="library-section saved-section"><div class="section-heading"><div><span class="eyebrow">BOOKMARKS</span><h2>Your reading list</h2></div><span class="count-pill">{len(diseases)} saved</span></div><div class="card-grid">{cards}</div></section>'
    return layout("Saved topics", content, "saved")


def study_page(diseases, greeting, response=None, question=None, selected=None, result=None, prompt=None):
    import study

    provider_note = (
        "A model provider is configured; its answers may be incomplete or incorrect. "
        "For personal medical concerns, consult a qualified health professional."
        if study.ai_provider_configured()
        else
        "No AI model is configured in this app, so replies use curated local study "
        "content. Set WELLNOTE_AI_API_KEY and WELLNOTE_AI_MODEL as described in "
        "README.md for general model-generated answers. For personal medical "
        "concerns, consult a qualified health professional."
    )
    lesson_cards = "".join(
        f'<a class="study-card" href="/study/{quote(item["slug"], safe="")}"><span class="study-card-icon">✎</span><span><small>{e(item["category"])}</small><strong>{e(item["name"])}</strong><em>Review key points →</em></span></a>'
        for item in diseases
    )
    exam_links = '<div class="exam-tags">' + "".join(
        f'<span><a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)} ↗</a></span>'
        for label, url in study.EXAM_SOURCES.values()
    ) + "</div>"
    response_html = ""
    if response:
        response_html = "<div class='chat-bubble reply'><span class='reply-label'>Study buddy</span>" + study_response_html(response) + "</div>"
    user_message = f"<div class='chat-bubble user-prompt'><span class='reply-label'>You asked</span><p>{e(prompt)}</p></div>" if prompt else ""
    bot = f"""<section class="tutor-card"><div class="tutor-heading"><span class="bot-avatar">✳</span><div><strong>Your study buddy</strong><small>Ready when you are</small></div><span class="online-dot"></span></div><div class="chat-bubble"><p>{e(greeting)}</p></div>{user_message}{response_html}<p class="tutor-hint">Try: “Help me plan for NEET”, “Explain biology”, “Help with homework”, or “Give me a study strategy.”</p><form action="/study/ask" method="post" class="prompt-form"><label class="sr-only" for="study-prompt">Ask a study question</label><textarea id="study-prompt" name="prompt" rows="3" placeholder="Ask a study question…"></textarea><button class="button button-dark" type="submit">Send <span>→</span></button></form><p class="scope-note">{e(provider_note)} Confirm exam requirements with official sources.</p>{exam_links}</section>"""
    if selected:
        intro = f'<section class="simple-hero"><a class="back-link" href="/study">← Study room</a><span class="eyebrow">FOCUSED REVIEW · {e(selected["category"])}</span><h1>{e(selected["name"])}<span class="brand-period">.</span></h1><p>Take a moment with the essentials, then revisit the full guide when you’re ready.</p></section>'
        points = "".join(f'<li class="study-point"><span class="point-number">{index:02d}</span><p>{e(point)}</p></li>' for index, point in enumerate(selected["study_points"], 1))
        main = f'<section class="study-content"><div class="study-notebook"><span class="eyebrow">THREE THINGS TO REMEMBER</span><ol class="study-points">{points}</ol><a class="button button-dark" href="/disease/{quote(selected["slug"], safe="")}">Read the full guide →</a></div><aside class="reflection-card"><span class="reflection-icon">✳</span><span class="eyebrow">REFLECT</span><h2>What would you like to ask a health professional?</h2><p>Use what you’ve learned to prepare questions for a conversation about your own health.</p></aside></section>'
        content = intro + main + bot + notice("Keep learning in context.", "Study notes summarize educational topics; they are not diagnostic tools or personal care recommendations.")
    elif question:
        options = "".join(f'<label class="answer-option"><input type="radio" name="answer" value="{i}" required>{"ABCD"[i]}. {e(option)}</label>' for i, option in enumerate(question["options"]))
        feedback = f'<div class="answer-feedback {"correct" if result == question["answer"] else "incorrect"}"><strong>{"Correct!" if result == question["answer"] else "Not quite—review the explanation."}</strong><p>{e(question["explanation"])}</p></div>' if result is not None else ""
        question_form = f'<div class="quiz-card"><span class="eyebrow">{e(question["subject"])} · ORIGINAL PRACTICE</span><h2>{e(question["question"])}</h2><form action="/study/answer/{e(question["id"])}" method="post" class="answer-form">{options}<button class="button button-dark" type="submit">Check answer</button></form>{feedback}<a class="button button-outline next-question" href="/study/question?after={quote(question["id"], safe="")}">Next question →</a></div>'
        content = f'<section class="simple-hero"><span class="eyebrow">PRACTICE, AT YOUR PACE</span><h1>One question at a time<span class="brand-period">.</span></h1><p>Original introductory examples. Check your reasoning with each explanation.</p></section><section class="practice-layout">{question_form}{bot}</section>{notice("Original practice only.", "These introductory questions are not official NEET, MCAT, or AAMC exam items and do not represent the full syllabus.")}'
    else:
        intro = '<section class="study-intro"><div><span class="eyebrow">A GENTLER WAY TO LEARN</span><h1>Welcome to your<br><span>study room.</span></h1><p>Short reviews, original practice, and a small study companion—no pressure, just a little more understanding.</p><a class="button button-dark" href="/study/question">Try a practice question →</a></div><div class="study-illustration" aria-hidden="true"><span class="study-plant">✳</span><span class="study-book">✎</span><span class="study-underline"></span></div></section>'
        main = f'<section class="study-content study-home"><div><div class="section-heading"><div><span class="eyebrow">YOUR TOPICS</span><h2>Choose what to review</h2><p>Essentials from each health guide.</p></div></div><div class="study-grid">{lesson_cards}</div><div class="exam-panel"><span class="eyebrow">EXAM STARTERS</span><h2>Preparing for an exam?</h2><p>Ask the study buddy about NEET, MCAT, or AAMC. For current exam details and syllabi, check the official provider.</p>{exam_links}</div></div>{bot}</section>{notice("Study, not a substitute.", "Study buddy replies are for education, not personal diagnosis or treatment. For your own symptoms or care, consult a qualified health professional.")}'
        content = intro + main
    return layout("Study room", content, "study")


def error_page(title, message, status="404 Not Found"):
    body = f'<section class="simple-hero"><span class="eyebrow">OOPS</span><h1>{e(title)}<span class="brand-period">.</span></h1><p>{e(message)}</p><a class="button button-dark" href="/">Back to explore →</a></section>'
    return status, layout(title, body)
