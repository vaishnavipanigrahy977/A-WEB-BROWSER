"""Escaped HTML rendering for the Python-led server-rendered app."""

from html import escape
import re
from urllib.parse import quote, quote_plus, urlencode

import translations


def e(value):
    return escape(str(value), quote=True)


def layout(title, content, active="home", language="en", current_url="/"):
    title = translations.translate(title, language)
    content = translations.translate_markup(content, language)
    links = [("home", "/", "Explore"), ("study", "/study", "Study room"), ("saved", "/saved", "Saved")]
    nav = "".join(
        f'<a class="nav-link{" active" if key == active else ""}" href="{href}">{translations.translate(label, language)}</a>'
        for key, href, label in links
    )
    language_links = []
    for selected, name in translations.LANGUAGES.items():
        current = ' aria-current="true"' if selected == language else ""
        language_url = e(urlencode({"lang": selected, "next": current_url}))
        language_links.append(f'<a{current} href="/language?{language_url}">{name}</a>')
    language_links = "".join(language_links)
    switcher = f'<nav class="language-switcher" aria-label="{e(translations.translate("Language switcher", language))}">{language_links}</nav>'
    translation_note = (
        f'<p class="language-note">{e(translations.translate("Some references and study content may still be in English.", language))}</p>'
        if language in ("hi", "hinglish") else ""
    )
    html_language = translations.LANGUAGE_HTML_CODES.get(language, "en")
    return f"""<!doctype html><html lang="{e(html_language)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f5f6ef"><title>{e(title)} · Wellnote</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet"><link rel="stylesheet" href="/static/style.css"><link rel="stylesheet" href="/static/language.css"></head><body><header class="site-header"><a class="brand" href="/"><span class="brand-mark">w</span><span>wellnote<span class="brand-period">.</span></span></a><nav class="main-nav" aria-label="Main navigation">{nav}</nav>{switcher}<span class="header-note"><span class="status-dot"></span>{e(translations.translate("A calmer way to learn", language))}</span></header><main>{content}</main><footer class="site-footer"><a class="brand footer-brand" href="/"><span class="brand-mark">w</span><span>wellnote<span class="brand-period">.</span></span></a><p>{e(translations.translate("Clearer health learning, one topic at a time.", language))}</p>{translation_note}<p class="footer-disclaimer">{e(translations.translate("For education only · Not a substitute for professional medical advice", language))}</p></footer></body></html>"""


def saved_topic_button(topic, saved_topics=(), language="en"):
    topic = topic.strip()[:120]
    already_saved = topic.casefold() in {item.casefold() for item in saved_topics}
    action = "remove-topic" if already_saved else "add-topic"
    icon = "♥" if already_saved else "＋"
    accessible_action = translations.translate(
        "Remove from library" if already_saved else "Save to library", language
    )
    return (
        f'<form class="topic-save-action" action="/saved/{action}" method="post">'
        f'<input type="hidden" name="topic" value="{e(topic)}">'
        f'<button class="save-button" type="submit" aria-label="{e(accessible_action)}: {e(topic)}">{icon}</button>'
        "</form>"
    )


def disease_card(disease, saved=False, language="en"):
    if disease.get("external"):
        topic = disease["external_topic"]
        href = f"/disease/{quote(topic, safe='')}"
        save_control = saved_topic_button(topic, (topic,) if saved else (), language)
        return (
            f'<article class="disease-card"><div class="card-topline">'
            f'<span class="category-label">{e(translations.translate("MedlinePlus reference", language))}</span>'
            f'{save_control}</div><a class="card-main" href="{e(href)}">'
            f'<h3>{e(disease["name"])}</h3><p>{e(translations.translate(disease["summary"], language))}</p>'
            f'<span class="text-link">{e(translations.translate("Explore topic", language))} <span>↗</span></span></a></article>'
        )
    slug = quote(disease["slug"], safe="")
    action = "remove" if saved else "add"
    icon = "♥" if saved else "＋"
    accessible_action = translations.translate(
        "Remove from library" if saved else "Save to library", language
    )
    return f"""<article class="disease-card"><div class="card-topline"><span class="category-label">{e(disease["category"])}</span><form action="/saved/{action}/{slug}" method="post"><button class="save-button" type="submit" aria-label="{e(accessible_action)}: {e(disease['name'])}">{icon}</button></form></div><a class="card-main" href="/disease/{slug}"><h3>{e(disease["name"])}</h3><p>{e(disease["summary"])}</p><span class="text-link">Explore topic <span>↗</span></span></a></article>"""


def reference_results(query, results, error=None, saved_topics=(), language="en"):
    if not results:
        detail = (
            f'<p>{e(error)}</p>' if error else
            "<p>MedlinePlus did not find a matching health topic. Try a broader search directly on the MedlinePlus website.</p>"
        )
        return f"""<section class="content-panel external-fallback"><span class="source-icon">↗</span><div><div class="reference-intro-header"><span class="eyebrow">MEDLINEPLUS REFERENCE</span>{saved_topic_button(query, saved_topics, language)}</div><h3>No reviewed Wellnote guide for “{e(query)}”</h3>{detail}<p>We won’t guess at symptoms or treatment. MedlinePlus is the U.S. National Library of Medicine’s health information service.</p><a class="button button-dark" href="https://medlineplus.gov/" target="_blank" rel="noopener noreferrer">Visit MedlinePlus ↗</a></div></section>"""
    items = "".join(
        f'<article class="content-panel reference-result"><span class="eyebrow">MEDLINEPLUS · NATIONAL LIBRARY OF MEDICINE</span><h3>{e(item["title"])}</h3><p>{e(item["summary"])}</p><a class="text-link" href="{e(item["url"])}" target="_blank" rel="noopener noreferrer">Read the full reference ↗</a>{saved_topic_button(item["title"], saved_topics, language)}</article>'
        for item in results
    )
    return f'<div class="reference-results"><section class="content-panel reference-intro"><div class="reference-intro-header"><span class="eyebrow">TRUSTED HEALTH REFERENCES</span>{saved_topic_button(query, saved_topics, language)}</div><h3>Information for “{e(query)}”</h3><p>These summaries are provided by MedlinePlus, a service of the U.S. National Library of Medicine. Open a source for its full article and references.</p></section>{items}</div>'


def home_page(diseases, query="", external_results=None, external_error=None, language="en", current_url="/", saved_topics=()):
    diseases = [translations.localize_disease(item, language) for item in diseases]
    cards = "".join(disease_card(item, language=language) for item in diseases)
    count_label = (
        f'{len(external_results)} {translations.translate("references", language)}'
        if query and external_results
        else translations.translate("External lookup", language)
        if query and not diseases
        else f'{len(diseases)} {translations.translate("topics", language)}'
    )
    if not cards:
        cards = reference_results(query, external_results or [], external_error, saved_topics, language)
    search = e(query)
    content = f"""<section class="hero"><div class="hero-copy"><span class="eyebrow"><span class="sparkle">✳</span>YOUR PERSONAL HEALTH LIBRARY</span><h1>Understand health.<br><span>Feel more prepared.</span></h1><p class="hero-description">Clear, thoughtful guides to health topics—made for learning, not self-diagnosis.</p><form class="search-form" action="/" method="get" role="search"><label class="sr-only" for="disease-search">Search health topics</label><span class="search-icon">⌕</span><input id="disease-search" type="search" name="q" value="{search}" placeholder="Search a disease or condition"><button type="submit">Search <span>→</span></button></form><p class="search-hint">Try “asthma”, “diabetes”, or “flu”</p></div><div class="hero-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="hero-sun"></div><div class="hero-leaf leaf-one"></div><div class="hero-leaf leaf-two"></div><div class="hero-note"><span class="note-icon">✳</span><span><strong>Knowledge is care</strong><small>Learn at your own pace</small></span></div><div class="hero-caption">A little more clarity,<br>a little less overwhelm.</div></div></section><section class="library-section"><div class="section-heading"><div><span class="eyebrow">THE LIBRARY</span><h2>{'Search results' if query else 'Explore health topics'}</h2><p>{f'Results for “{search}”' if query else 'Start with a topic, follow your curiosity.'}</p></div><span class="count-pill">{count_label}</span></div><div class="card-grid">{cards}</div></section><section class="study-banner"><div class="study-symbol">✎</div><div><span class="eyebrow">MAKE IT STICK</span><h2>Curiosity, meet your study room.</h2><p>Review health topics, ask the study buddy, and practice original questions.</p></div><a class="button button-dark" href="/study">Visit study room <span>→</span></a></section>{notice('A note on health information', 'These guides are educational, not medical advice. They cover a small set of common topics, not every disease. Always talk with a qualified health professional about personal symptoms or care.')}"""
    return layout("Explore health topics", content, language=language, current_url=current_url)


def external_topic_page(topic, results=None, error=None, language="en", current_url="/", saved_topics=()):
    """Render linked NLM references or a clear fallback without inventing facts."""
    content = f"""<section class="simple-hero"><a class="back-link" href="/">← All topics</a><span class="eyebrow">EXTERNAL HEALTH REFERENCE</span><h1>{e(topic)}<span class="brand-period">.</span></h1><p>This condition is not in Wellnote’s small, reviewed starter library.</p></section>{reference_results(topic, results or [], error, saved_topics, language)}{notice('For education, not diagnosis.', 'Online references cannot assess your personal health. For symptoms or care, talk with a qualified health professional; for a possible emergency, contact local emergency services.')}"""
    return layout(f"Find information about {topic}", content, language=language, current_url=current_url)


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


def disease_page(disease, saved=False, language="en", current_url="/"):
    disease = translations.localize_disease(disease, language)
    bullets = lambda values: "".join(f"<li>{e(value)}</li>" for value in values)
    action = "remove" if saved else "add"
    save_label = "♥ Saved to your library" if saved else "＋ Save for later"
    points = bullets(disease["study_points"])
    content = f"""<section class="detail-hero"><a class="back-link" href="/">← All topics</a><span class="eyebrow">{e(disease["category"])}</span><div class="detail-title-row"><div><h1>{e(disease["name"])}</h1><p class="detail-summary">{e(disease["summary"])}</p></div><form action="/saved/{action}/{quote(disease['slug'], safe='')}" method="post"><button class="button button-save">{save_label}</button></form></div></section><div class="detail-layout"><article class="detail-article"><section class="content-panel"><span class="eyebrow">THE OVERVIEW</span><h2>What it is</h2><p>{e(disease["description"])}</p></section><section class="content-panel"><div class="panel-heading"><span class="panel-icon icon-coral">✳</span><div><span class="eyebrow">WHAT TO LOOK FOR</span><h2>Common symptoms</h2></div></div><ul class="check-list">{bullets(disease["symptoms"])}</ul><p class="quiet-note">Symptoms can vary. This list cannot tell you what is causing your symptoms.</p></section><section class="content-panel"><div class="panel-heading"><span class="panel-icon icon-green">↗</span><div><span class="eyebrow">EVERYDAY WELLBEING</span><h2>Prevention &amp; risk reduction</h2></div></div><ul class="check-list">{bullets(disease["prevention"])}</ul></section><section class="content-panel treatment-panel"><div class="panel-heading"><span class="panel-icon icon-blue">✚</span><div><span class="eyebrow">CARE &amp; TREATMENT</span><h2>Can it be treated?</h2></div></div><p>{e(disease["treatment"])}</p><div class="care-callout"><span>♡</span><p>Care is personal. A licensed health professional can help you understand your options and what is right for you.</p></div></section><section class="source-panel"><span class="source-icon">↗</span><p>Learn more from <a href="{e(disease['source_url'])}" target="_blank" rel="noopener noreferrer">{e(disease["source_name"])} ↗</a></p></section></article><aside class="study-sidebar"><div class="sidebar-card"><span class="eyebrow">QUICK REVIEW</span><h3>Key takeaways</h3><ul>{points}</ul><a class="text-link" href="/study/{quote(disease['slug'], safe='')}">Study this topic →</a></div><div class="urgent-card"><span class="urgent-icon">!</span><p><strong>Need medical help?</strong><br>If you think you may have a medical emergency, contact your local emergency services now.</p></div></aside></div>{notice('Learning, not diagnosis.', 'This overview is general education and is not a substitute for a clinician’s assessment, diagnosis, or treatment advice.')}"""
    return layout(disease["name"], content, language=language, current_url=current_url)


def saved_page(diseases, language="en", current_url="/"):
    diseases = [translations.localize_disease(item, language) for item in diseases]
    saved_count = f'{len(diseases)} {translations.translate("saved", language)}'
    cards = "".join(disease_card(item, saved=True, language=language) for item in diseases)
    if not cards:
        cards = '<div class="empty-state"><span class="empty-icon">♡</span><h3>Your library is ready</h3><p>Save a health topic to keep it close for your next study session.</p><a class="button button-outline" href="/">Explore health topics</a></div>'
    content = f'<section class="simple-hero"><span class="eyebrow">YOUR PERSONAL LIBRARY</span><h1>Saved topics<span class="brand-period">.</span></h1><p>Pick up where your curiosity left off.</p></section><section class="library-section saved-section"><div class="section-heading"><div><span class="eyebrow">BOOKMARKS</span><h2>Your reading list</h2></div><span class="count-pill">{e(saved_count)}</span></div><div class="card-grid">{cards}</div></section>'
    return layout("Saved topics", content, "saved", language, current_url)


def mind_map_page(diseases, topic="", selected=None, reference=None, reference_error=None, language="en", current_url="/", saved_topics=()):
    import study

    selected = translations.localize_disease(selected, language) if selected else None
    topic_value = selected["name"] if selected else topic
    picker = f"""<form action="/study/mind-map" method="get" class="mind-map-picker"><label for="mind-map-topic">Enter any disease or health topic</label><div><input id="mind-map-topic" name="topic" type="search" value="{e(topic_value)}" placeholder="For example: malaria, lupus, or asthma" maxlength="120" required><button class="button button-dark" type="submit">Generate map</button></div></form>"""
    diagram = ""
    if topic_value:
        if selected:
            branches = study.create_mind_map(selected)
            title = selected["name"]
            summary = selected["summary"]
            source = f"""Based on Wellnote’s educational guide. <a href="{e(selected["source_url"])}" target="_blank" rel="noopener noreferrer">Read {e(selected["source_name"])} ↗</a>"""
        else:
            branches = study.create_reference_mind_map(topic_value, reference)
            title = topic_value
            summary = (
                "Available details from the reference appear in the branches below."
                if branches else
                "No source details were available for branches; use the linked article to research this topic."
                if reference else
                "No matching MedlinePlus article was found, so only the topic node is shown."
            )
            source = (
                f"""Based on a MedlinePlus search result. <a href="{e(reference["url"])}" target="_blank" rel="noopener noreferrer">Read {e(reference["title"])} ↗</a>"""
                if reference else
                f"""No MedlinePlus article was found{f": {e(reference_error)}" if reference_error else ""}. <a href="https://medlineplus.gov/" target="_blank" rel="noopener noreferrer">Search MedlinePlus ↗</a>"""
            )
        branch_cards = []
        for branch in branches:
            points = "".join(f"<li>{e(point)}</li>" for point in branch["points"])
            detail_link = ""
            if not selected and reference:
                detail_link = (
                    f'<a class="mind-map-detail-link" href="{e(reference["url"])}" '
                    'target="_blank" rel="noopener noreferrer">Open the full article for details ↗</a>'
                )
            elif not selected:
                detail_link = (
                    f'<a class="mind-map-detail-link" href="/?q={quote_plus(topic_value)}">'
                    "Search MedlinePlus for details ↗</a>"
                )
            branch_cards.append(
                f'<section class="mind-map-branch"><h3>{e(branch["title"])}</h3>'
                f"<ul>{points}</ul>{detail_link}</section>"
            )
        save_control = (
            saved_topic_button(reference["title"] if reference else topic_value, saved_topics, language)
            if not selected else ""
        )
        diagram = f"""<section class="mind-map-canvas" aria-label="Mind map for {e(title)}"><div class="mind-map-root"><span class="eyebrow">STUDY TOPIC</span><h2>{e(title)}</h2><p>{e(summary)}</p></div><div class="mind-map-branches">{"".join(branch_cards)}</div></section><p class="mind-map-source">{source}</p>{save_control}"""
    content = f"""<section class="simple-hero"><a class="back-link" href="/study">← Study room</a><span class="eyebrow">VISUAL STUDY TOOL</span><h1>Mind map generator<span class="brand-period">.</span></h1><p>Enter any health topic. Wellnote uses its reviewed guide or searches MedlinePlus for a reference.</p></section>{picker}{diagram}{notice("Learning, not diagnosis.", "Maps outside Wellnote’s reviewed guides use linked references or clearly labeled study prompts. They are educational and not personal medical advice.")}"""
    return layout("Mind map generator", content, "study", language, current_url)


def flashcards_page(topic="", selected=None, reference=None, cards=None, card_index=0, reference_error=None, language="en", current_url="/", saved_topics=()):
    selected = translations.localize_disease(selected, language) if selected else None
    cards = cards or []
    topic_value = selected["name"] if selected else topic
    picker = f"""<form action="/study/flashcards" method="get" class="mind-map-picker"><label for="flashcard-topic">Choose any disease or health topic</label><div><input id="flashcard-topic" name="topic" type="search" value="{e(topic_value)}" placeholder="For example: asthma, malaria, or diabetes" maxlength="120" required><button class="button button-dark" type="submit">Build deck</button></div></form>"""
    card_html = ""
    save_control = (
        saved_topic_button(reference["title"] if reference else topic_value, saved_topics, language)
        if topic_value and not selected else ""
    )
    if cards:
        card = cards[card_index]
        answer = "".join(f"<li>{e(item)}</li>" for item in card["answer"])
        if selected:
            source_link = f"""<a class="flashcard-source" href="{e(selected["source_url"])}" target="_blank" rel="noopener noreferrer">Review {e(selected["source_name"])} ↗</a>"""
            topic_param = selected["slug"]
        else:
            source_link = f"""<a class="flashcard-source" href="{e(reference["url"])}" target="_blank" rel="noopener noreferrer">Read the MedlinePlus article ↗</a>"""
            topic_param = topic_value
        previous = (card_index - 1) % len(cards)
        next_card = (card_index + 1) % len(cards)
        card_html = f"""<section class="flashcard-panel"><div class="flashcard-progress"><span class="eyebrow">CARD {card_index + 1} OF {len(cards)}</span><span>{e(card.get("category", "REVIEW"))}</span></div><div class="flashcard-front"><span class="eyebrow">QUESTION</span><h2>{e(card["question"])}</h2></div><details class="flashcard-reveal"><summary>Reveal answer</summary><div class="flashcard-back"><ul>{answer}</ul>{source_link}</div></details><nav class="flashcard-navigation" aria-label="Flashcard navigation"><a class="button button-outline" href="/study/flashcards?topic={quote_plus(topic_param)}&amp;card={previous}">← Previous</a><a class="button button-dark" href="/study/flashcards?topic={quote_plus(topic_param)}&amp;card={next_card}">Next card →</a></nav></section>"""
    elif topic_value:
        detail = (
            f"No MedlinePlus article was found{f': {e(reference_error)}' if reference_error else ''}. "
            "No factual flashcards were generated."
        )
        card_html = f"""<section class="content-panel flashcard-empty"><h2>No reviewed flashcards available</h2><p>{e(detail)}</p><a class="text-link" href="https://medlineplus.gov/" target="_blank" rel="noopener noreferrer">Search MedlinePlus ↗</a></section>"""
    content = f"""<section class="simple-hero"><a class="back-link" href="/study">← Study room</a><span class="eyebrow">ACTIVE RECALL</span><h1>Smart flashcards<span class="brand-period">.</span></h1><p>Choose any topic, try to recall the answer, then reveal it and move through the deck.</p></section>{picker}{save_control}{card_html}{notice("Learn safely.", "Cards summarize Wellnote educational guides or linked MedlinePlus references. They are for study, not personal diagnosis or treatment.")}"""
    return layout("Smart flashcards", content, "study", language, current_url)


def disease_comparison_page(first="", second="", left=None, right=None, error=None, language="en", current_url="/"):
    left = translations.localize_comparison(left, language)
    right = translations.localize_comparison(right, language)
    picker = f"""<form action="/study/compare" method="get" class="comparison-picker"><label for="compare-first">First health topic</label><input id="compare-first" name="first" type="search" value="{e(first)}" placeholder="For example: asthma" maxlength="120" required><label for="compare-second">Second health topic</label><input id="compare-second" name="second" type="search" value="{e(second)}" placeholder="For example: seasonal flu" maxlength="120" required><button class="button button-dark" type="submit">Compare topics</button></form>"""
    results = ""
    if error:
        results = f'<p class="comparison-error" role="alert">{e(error)}</p>'
    elif left and right:
        def render_cell(data, key):
            items = "".join(f"<li>{e(value)}</li>" for value in data[key])
            return f"<ul>{items}</ul>"

        rows = []
        for key, label in (
            ("overview", "Overview"),
            ("symptoms", "Symptoms"),
            ("prevention", "Prevention"),
            ("treatment", "Treatment & care"),
        ):
            rows.append(
                f"<tr><th scope=\"row\">{e(label)}</th>"
                f"<td>{render_cell(left, key)}</td><td>{render_cell(right, key)}</td></tr>"
            )
        sources = (
            f'<tr><th scope="row">Sources</th><td><a href="{e(left["source_url"])}" target="_blank" rel="noopener noreferrer">{e(left["source_name"])} ↗</a></td>'
            f'<td><a href="{e(right["source_url"])}" target="_blank" rel="noopener noreferrer">{e(right["source_name"])} ↗</a></td></tr>'
        )
        results = f"""<div class="comparison-table-wrap"><table class="comparison-table"><thead><tr><th scope="col">Compare</th><th scope="col">{e(left["name"])}</th><th scope="col">{e(right["name"])}</th></tr></thead><tbody>{"".join(rows)}{sources}</tbody></table></div>"""
    content = f"""<section class="simple-hero"><a class="back-link" href="/study">← Study room</a><span class="eyebrow">SIDE-BY-SIDE REVIEW</span><h1>Disease comparison<span class="brand-period">.</span></h1><p>Compare two health topics using reviewed Wellnote guides or linked MedlinePlus references.</p></section>{picker}{results}{notice("Compare for learning, not diagnosis.", "Topics can differ in important ways beyond this summary. This comparison cannot determine what condition a person has or which treatment is right for them.")}"""
    return layout("Disease comparison", content, "study", language, current_url)


def study_page(diseases, greeting, response=None, question=None, selected=None, result=None, prompt=None, language="en", current_url="/"):
    import study

    diseases = [translations.localize_disease(item, language) for item in diseases]
    selected = translations.localize_disease(selected, language) if selected else None
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
    voice_tools = """<div class="voice-tools"><button class="button button-outline" id="voice-read" type="button">Read answer aloud</button><button class="button button-outline" id="voice-stop" type="button">Stop audio</button></div><p class="voice-status" id="voice-status" role="status" aria-live="polite">Select Read answer aloud to hear the study buddy response.</p>"""
    bot = f"""<section class="tutor-card"><div class="tutor-heading"><span class="bot-avatar">✳</span><div><strong>Your study buddy</strong><small>Ready when you are</small></div><span class="online-dot"></span></div><div class="chat-bubble"><p>{e(greeting)}</p></div>{user_message}{response_html}<p class="tutor-hint">Try: “Help me plan for NEET”, “Explain biology”, “Help with homework”, or “Give me a study strategy.”</p><form action="/study/ask" method="post" class="prompt-form"><label class="sr-only" for="study-prompt">Ask a study question</label><textarea id="study-prompt" name="prompt" rows="3" placeholder="Ask a study question…"></textarea><button class="button button-dark" type="submit">Send <span>→</span></button></form>{voice_tools}<p class="scope-note">{e(provider_note)} Confirm exam requirements with official sources.</p>{exam_links}</section>"""
    if selected:
        intro = f'<section class="simple-hero"><a class="back-link" href="/study">← Study room</a><span class="eyebrow">FOCUSED REVIEW · {e(selected["category"])}</span><h1>{e(selected["name"])}<span class="brand-period">.</span></h1><p>Take a moment with the essentials, then revisit the full guide when you’re ready.</p></section>'
        points = "".join(f'<li class="study-point"><span class="point-number">{index:02d}</span><p>{e(point)}</p></li>' for index, point in enumerate(selected["study_points"], 1))
        main = f'<section class="study-content"><div class="study-notebook"><span class="eyebrow">THREE THINGS TO REMEMBER</span><ol class="study-points">{points}</ol><a class="button button-dark" href="/disease/{quote(selected["slug"], safe="")}">Read the full guide →</a> <a class="button button-outline" href="/study/mind-map?topic={quote(selected["slug"], safe="")}">Make a mind map</a> <a class="button button-outline" href="/study/flashcards?topic={quote(selected["slug"], safe="")}">Study with flashcards</a> <a class="button button-outline" href="/study/compare?first={quote_plus(selected["name"])}">Compare with another topic</a></div><aside class="reflection-card"><span class="reflection-icon">✳</span><span class="eyebrow">REFLECT</span><h2>What would you like to ask a health professional?</h2><p>Use what you’ve learned to prepare questions for a conversation about your own health.</p></aside></section>'
        content = intro + main + bot + notice("Keep learning in context.", "Study notes summarize educational topics; they are not diagnostic tools or personal care recommendations.")
    elif question:
        options = "".join(f'<label class="answer-option"><input type="radio" name="answer" value="{i}" required>{"ABCD"[i]}. {e(option)}</label>' for i, option in enumerate(question["options"]))
        feedback = f'<div class="answer-feedback {"correct" if result == question["answer"] else "incorrect"}"><strong>{"Correct!" if result == question["answer"] else "Not quite—review the explanation."}</strong><p>{e(question["explanation"])}</p></div>' if result is not None else ""
        question_form = f'<div class="quiz-card"><span class="eyebrow">{e(question["subject"])} · ORIGINAL PRACTICE</span><h2>{e(question["question"])}</h2><form action="/study/answer/{e(question["id"])}" method="post" class="answer-form">{options}<button class="button button-dark" type="submit">Check answer</button></form>{feedback}<a class="button button-outline next-question" href="/study/question?after={quote(question["id"], safe="")}">Next question →</a></div>'
        content = f'<section class="simple-hero"><span class="eyebrow">PRACTICE, AT YOUR PACE</span><h1>One question at a time<span class="brand-period">.</span></h1><p>Original introductory examples. Check your reasoning with each explanation.</p></section><section class="practice-layout">{question_form}{bot}</section>{notice("Original practice only.", "These introductory questions are not official NEET, MCAT, or AAMC exam items and do not represent the full syllabus.")}'
    else:
        intro = '<section class="study-intro"><div><span class="eyebrow">A GENTLER WAY TO LEARN</span><h1>Welcome to your<br><span>study room.</span></h1><p>Short reviews, original practice, and a small study companion—no pressure, just a little more understanding.</p><div class="study-actions"><a class="button button-dark" href="/study/question">Try a practice question →</a><a class="button button-outline" href="/study/mind-map">Generate a mind map</a><a class="button button-outline" href="/study/flashcards">Smart flashcards</a><a class="button button-outline" href="/study/compare">Compare diseases</a></div></div><div class="study-illustration" aria-hidden="true"><span class="study-plant">✳</span><span class="study-book">✎</span><span class="study-underline"></span></div></section>'
        main = f'<section class="study-content study-home"><div><div class="section-heading"><div><span class="eyebrow">YOUR TOPICS</span><h2>Choose what to review</h2><p>Essentials from each health guide.</p></div></div><div class="study-grid">{lesson_cards}</div><div class="exam-panel"><span class="eyebrow">EXAM STARTERS</span><h2>Preparing for an exam?</h2><p>Ask the study buddy about NEET, MCAT, or AAMC. For current exam details and syllabi, check the official provider.</p>{exam_links}</div></div>{bot}</section>{notice("Study, not a substitute.", "Study buddy replies are for education, not personal diagnosis or treatment. For your own symptoms or care, consult a qualified health professional.")}'
        content = intro + main
    content += '<script src="/static/voice-tutor.js" defer></script>'
    return layout("Study room", content, "study", language, current_url)


def error_page(title, message, status="404 Not Found", language="en", current_url="/"):
    body = f'<section class="simple-hero"><span class="eyebrow">OOPS</span><h1>{e(title)}<span class="brand-period">.</span></h1><p>{e(message)}</p><a class="button button-dark" href="/">Back to explore →</a></section>'
    return status, layout(title, body, language=language, current_url=current_url)
