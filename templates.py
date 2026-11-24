"""Escaped HTML rendering for the Python-led server-rendered app."""

from html import escape
import json
import re
from urllib.parse import quote, quote_plus, urlencode

import translations
import body_verse
import openstax


def e(value):
    return escape(str(value), quote=True)


def layout(title, content, active="home", language="en", current_url="/", extra_styles=""):
    import study

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
        language_links.append(
            f'<a{current} href="/language?{language_url}">'
            f'{e(translations.translate(name, language))}</a>'
        )
    language_links = "".join(language_links)
    switcher = f'<nav class="language-switcher" aria-label="{e(translations.translate("Language switcher", language))}">{language_links}</nav>'
    translation_note = (
        f'<p class="language-note">{e(translations.translate("Some references and study content may still be in English.", language))}</p>'
        if language in ("hi", "hinglish") else ""
    )
    html_language = translations.LANGUAGE_HTML_CODES.get(language, "en")
    voice_messages = {
        "voice_unsupported": "Spoken answers are not supported in this browser.",
        "voice_ask_first": "Ask a question first, then your answer can be read aloud.",
        "voice_loading": "Checking for the right speech voice…",
        "voice_missing": "Install a {language} speech voice in your device’s language or speech settings, then try again.",
        "voice_cloud_loading": "Creating speech with Gemini…",
        "voice_reading": "Reading the answer aloud.",
        "voice_finished": "Finished reading the answer.",
        "voice_error": "Audio playback stopped or is unavailable.",
        "voice_stopped": "Audio stopped.",
        "voice_english_name": "English",
        "voice_hindi_name": "Hindi",
        "voice_hinglish_name": "Hindi for Hinglish",
    }
    voice_data = " ".join(
        f'data-{name.replace("_", "-")}="{e(translations.translate(message, language))}"'
        for name, message in voice_messages.items()
    )
    voice_data += (
        f' data-voice-gemini-enabled="{str(study.gemini_speech_configured()).lower()}"'
    )
    return f"""<!doctype html><html lang="{e(html_language)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f5f6ef"><title>{e(title)} · WellNote</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet"><link rel="stylesheet" href="/static/style.css"><link rel="stylesheet" href="/static/language.css">{extra_styles}</head><body {voice_data}><header class="site-header"><a class="brand" href="/"><span class="brand-mark">w</span><span>WellNote<span class="brand-period">.</span></span></a><nav class="main-nav" aria-label="{e(translations.translate("Main navigation", language))}">{nav}</nav>{switcher}<span class="header-note"><span class="status-dot"></span>{e(translations.translate("A calmer way to learn", language))}</span></header><main>{content}</main><footer class="site-footer"><a class="brand footer-brand" href="/"><span class="brand-mark">w</span><span>WellNote<span class="brand-period">.</span></span></a><p>{e(translations.translate("Clearer health learning, one topic at a time.", language))}</p>{translation_note}<p class="footer-disclaimer">{e(translations.translate("For education only · Not a substitute for professional medical advice", language))}</p></footer></body></html>"""


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
        no_guide = e(translations.translate_format(
            "No reviewed WellNote guide for “{query}”", language, query=query
        ))
        return f"""<section class="content-panel external-fallback"><span class="source-icon">↗</span><div><div class="reference-intro-header"><span class="eyebrow">MEDLINEPLUS REFERENCE</span>{saved_topic_button(query, saved_topics, language)}</div><h3>{no_guide}</h3>{detail}<p>We won’t guess at symptoms or treatment. MedlinePlus is the U.S. National Library of Medicine’s health information service.</p><a class="button button-dark" href="https://medlineplus.gov/" target="_blank" rel="noopener noreferrer">Visit MedlinePlus ↗</a></div></section>"""
    items = "".join(
        f'<article class="content-panel reference-result"><span class="eyebrow">MEDLINEPLUS · NATIONAL LIBRARY OF MEDICINE</span><h3>{e(item["title"])}</h3><p>{e(item["summary"])}</p><a class="text-link" href="{e(item["url"])}" target="_blank" rel="noopener noreferrer">Read the full reference ↗</a>{saved_topic_button(item["title"], saved_topics, language)}</article>'
        for item in results
    )
    information_title = e(translations.translate_format(
        "Information for “{query}”", language, query=query
    ))
    return f'<div class="reference-results"><section class="content-panel reference-intro"><div class="reference-intro-header"><span class="eyebrow">TRUSTED HEALTH REFERENCES</span>{saved_topic_button(query, saved_topics, language)}</div><h3>{information_title}</h3><p>These summaries are provided by MedlinePlus, a service of the U.S. National Library of Medicine. Open a source for its full article and references.</p></section>{items}</div>'


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
    result_description = (
        translations.translate_format("Results for “{query}”", language, query=search)
        if query else "Start with a topic, follow your curiosity."
    )
    content = f"""<section class="hero"><div class="hero-copy"><span class="eyebrow"><span class="sparkle">✳</span>YOUR PERSONAL HEALTH LIBRARY</span><h1>Understand health.<br><span>Feel more prepared.</span></h1><p class="hero-description">Clear, thoughtful guides to health topics—made for learning, not self-diagnosis.</p><form class="search-form" action="/" method="get" role="search"><label class="sr-only" for="disease-search">Search health topics</label><span class="search-icon">⌕</span><input id="disease-search" type="search" name="q" value="{search}" placeholder="Search a disease or condition"><button type="submit">Search <span>→</span></button></form><p class="search-hint">Try “asthma”, “diabetes”, or “flu”</p></div><div class="hero-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="hero-sun"></div><div class="hero-leaf leaf-one"></div><div class="hero-leaf leaf-two"></div><div class="hero-note"><span class="note-icon">✳</span><span><strong>Knowledge is care</strong><small>Learn at your own pace</small></span></div><div class="hero-caption">A little more clarity,<br>a little less overwhelm.</div></div></section><section class="library-section"><div class="section-heading"><div><span class="eyebrow">THE LIBRARY</span><h2>{'Search results' if query else 'Explore health topics'}</h2><p>{result_description}</p></div><span class="count-pill">{count_label}</span></div><div class="card-grid">{cards}</div></section><section class="study-banner"><div class="study-symbol">✎</div><div><span class="eyebrow">MAKE IT STICK</span><h2>Curiosity, meet your study room.</h2><p>Review health topics, ask the study buddy, and practice original questions.</p></div><a class="button button-dark" href="/study">Visit study room <span>→</span></a></section>{notice('A note on health information', 'These guides are educational, not medical advice. They cover a small set of common topics, not every disease. Always talk with a qualified health professional about personal symptoms or care.')}"""
    return layout("Explore health topics", content, language=language, current_url=current_url)


def video_preview(video, topic, error=None, origin=""):
    if video:
        video_id = quote(video["video_id"], safe="")
        embed_query = urlencode({"rel": "0", "origin": origin})
        return (
            '<section class="video-preview-card"><span class="eyebrow">WATCH &amp; LEARN</span>'
            '<h3>Animated explainer</h3><div class="video-frame">'
            f'<iframe src="https://www.youtube-nocookie.com/embed/{video_id}?{e(embed_query)}" '
            f'title="{e(video["title"])}" loading="lazy" referrerpolicy="origin" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            f'allowfullscreen></iframe></div><p class="video-attribution">'
            f'<a href="https://www.youtube.com/watch?v={video_id}" target="_blank" rel="noopener noreferrer">'
            f'{e(video["title"])} ↗</a><span>by {e(video["channel"])} · YouTube</span></p>'
            '<p class="video-note">Supplementary educational content; it may not cover every detail in the reference.</p></section>'
        )

    video_query = quote_plus(f"{topic} animated medical explanation")
    status = (
        "YouTube could not be reached just now."
        if error else "No topic-matched video preview was found."
    )
    return (
        '<section class="video-preview-card"><span class="eyebrow">WATCH &amp; LEARN</span>'
        f'<h3>Video preview unavailable</h3><p class="video-note">{e(status)}</p>'
        f'<a class="text-link" href="https://www.youtube.com/results?search_query={video_query}" '
        'target="_blank" rel="noopener noreferrer">Search YouTube for an explainer ↗</a></section>'
    )


def external_topic_page(topic, results=None, error=None, language="en", current_url="/", saved_topics=(), video=None, video_error=None, origin=""):
    """Render linked NLM references or a clear fallback without inventing facts."""
    references = reference_results(topic, results or [], error, saved_topics, language)
    content = f"""<section class="simple-hero"><a class="back-link" href="/">← All topics</a><span class="eyebrow">EXTERNAL HEALTH REFERENCE</span><h1>{e(topic)}<span class="brand-period">.</span></h1><p>This condition is not in WellNote’s small, reviewed starter library.</p></section><div class="external-topic-layout"><div class="external-topic-content">{references}</div><aside class="study-sidebar">{video_preview(video, topic, video_error, origin)}</aside></div>{notice('For education, not diagnosis.', 'Online references cannot assess your personal health. For symptoms or care, talk with a qualified health professional; for a possible emergency, contact local emergency services.')}"""
    title = translations.translate_format(
        "Find information about {topic}", language, topic=topic
    )
    return layout(title, content, language=language, current_url=current_url)


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


def disease_page(disease, saved=False, language="en", current_url="/", video=None, video_error=None, origin=""):
    disease = translations.localize_disease(disease, language)
    bullets = lambda values: "".join(f"<li>{e(value)}</li>" for value in values)
    action = "remove" if saved else "add"
    save_label = "♥ Saved to your library" if saved else "＋ Save for later"
    points = bullets(disease["study_points"])
    if video is None and disease.get("video_id"):
        video = {
            "video_id": disease["video_id"],
            "title": disease["video_title"],
            "channel": disease["video_channel"],
        }
    video_panel = video_preview(video, disease["name"], video_error, origin)
    content = f"""<section class="detail-hero"><a class="back-link" href="/">← All topics</a><span class="eyebrow">{e(disease["category"])}</span><div class="detail-title-row"><div><h1>{e(disease["name"])}</h1><p class="detail-summary">{e(disease["summary"])}</p></div><form action="/saved/{action}/{quote(disease['slug'], safe='')}" method="post"><button class="button button-save">{save_label}</button></form></div></section><div class="detail-layout"><article class="detail-article"><section class="content-panel"><span class="eyebrow">THE OVERVIEW</span><h2>What it is</h2><p>{e(disease["description"])}</p></section><section class="content-panel"><div class="panel-heading"><span class="panel-icon icon-coral">✳</span><div><span class="eyebrow">WHAT TO LOOK FOR</span><h2>Common symptoms</h2></div></div><ul class="check-list">{bullets(disease["symptoms"])}</ul><p class="quiet-note">Symptoms can vary. This list cannot tell you what is causing your symptoms.</p></section><section class="content-panel"><div class="panel-heading"><span class="panel-icon icon-green">↗</span><div><span class="eyebrow">EVERYDAY WELLBEING</span><h2>Prevention &amp; risk reduction</h2></div></div><ul class="check-list">{bullets(disease["prevention"])}</ul></section><section class="content-panel treatment-panel"><div class="panel-heading"><span class="panel-icon icon-blue">✚</span><div><span class="eyebrow">CARE &amp; TREATMENT</span><h2>Can it be treated?</h2></div></div><p>{e(disease["treatment"])}</p><div class="care-callout"><span>♡</span><p>Care is personal. A licensed health professional can help you understand your options and what is right for you.</p></div></section><section class="source-panel"><span class="source-icon">↗</span><p>Learn more from <a href="{e(disease['source_url'])}" target="_blank" rel="noopener noreferrer">{e(disease["source_name"])} ↗</a></p></section></article><aside class="study-sidebar">{video_panel}<div class="sidebar-card"><span class="eyebrow">QUICK REVIEW</span><h3>Key takeaways</h3><ul>{points}</ul><a class="text-link" href="/study/{quote(disease['slug'], safe='')}">Study this topic →</a></div><div class="urgent-card"><span class="urgent-icon">!</span><p><strong>Need medical help?</strong><br>If you think you may have a medical emergency, contact your local emergency services now.</p></div></aside></div>{notice('Learning, not diagnosis.', 'This overview is general education and is not a substitute for a clinician’s assessment, diagnosis, or treatment advice.')}"""
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
            source = (
                f'{e(translations.translate("Based on WellNote’s educational guide.", language))} '
                f'<a href="{e(selected["source_url"])}" target="_blank" rel="noopener noreferrer">'
                f'{e(translations.translate("Read", language))} {e(selected["source_name"])} ↗</a>'
            )
        else:
            branches = translations.localize_reference_branches(
                study.create_reference_mind_map(topic_value, reference),
                topic_value,
                language,
            )
            title = topic_value
            summary = (
                "Available details from the reference appear in the branches below."
                if branches else
                "No source details were available for branches; use the linked article to research this topic."
                if reference else
                "No matching MedlinePlus article was found, so only the topic node is shown."
            )
            source = (
                f'{e(translations.translate("Based on a MedlinePlus search result.", language))} '
                f'<a href="{e(reference["url"])}" target="_blank" rel="noopener noreferrer">'
                f'{e(translations.translate("Read", language))} {e(reference["title"])} ↗</a>'
                if reference else
                f'{e(translations.translate("No MedlinePlus article was found", language))}'
                f'{f": {e(reference_error)}" if reference_error else ""}. '
                f'<a href="https://medlineplus.gov/" target="_blank" rel="noopener noreferrer">'
                f'{e(translations.translate("Search MedlinePlus ↗", language))}</a>'
            )
        branch_cards = []
        for branch in branches:
            points = "".join(f"<li>{e(point)}</li>" for point in branch["points"])
            detail_link = ""
            if not selected and reference:
                detail_link = (
                    f'<a class="mind-map-detail-link" href="{e(reference["url"])}" '
                    f'target="_blank" rel="noopener noreferrer">'
                    f'{e(translations.translate("Open the full article for details ↗", language))}</a>'
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
        map_label = e(translations.translate_format(
            "Mind map for {topic}", language, topic=title
        ))
        diagram = f"""<section class="mind-map-canvas" aria-label="{map_label}"><div class="mind-map-root"><span class="eyebrow">STUDY TOPIC</span><h2>{e(title)}</h2><p>{e(summary)}</p></div><div class="mind-map-branches">{"".join(branch_cards)}</div></section><p class="mind-map-source">{source}</p>{save_control}"""
    content = f"""<section class="simple-hero"><a class="back-link" href="/study">← Study room</a><span class="eyebrow">VISUAL STUDY TOOL</span><h1>Mind map generator<span class="brand-period">.</span></h1><p>Enter any health topic. WellNote uses its reviewed guide or searches MedlinePlus for a reference.</p></section>{picker}{diagram}{notice("Learning, not diagnosis.", "Maps outside WellNote’s reviewed guides use linked references or clearly labeled study prompts. They are educational and not personal medical advice.")}"""
    return layout("Mind map generator", content, "study", language, current_url)


def flashcards_page(topic="", selected=None, reference=None, cards=None, card_index=0, reference_error=None, language="en", current_url="/", saved_topics=()):
    import study

    selected = translations.localize_disease(selected, language) if selected else None
    if selected and language in ("hi", "hinglish"):
        cards = study.create_flashcards(selected)
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
        category = translations.translate(card.get("category", "REVIEW"), language)
        progress = translations.translate_format(
            "CARD {current} OF {total}",
            language,
            current=card_index + 1,
            total=len(cards),
        )
        flashcard_question = translations.localize_flashcard_question(
            card, topic_value, language
        )
        if selected:
            source_link = (
                f'<a class="flashcard-source" href="{e(selected["source_url"])}" '
                f'target="_blank" rel="noopener noreferrer">'
                f'{e(translations.translate("Review", language))} '
                f'{e(selected["source_name"])} ↗</a>'
            )
            topic_param = selected["slug"]
        else:
            source_link = (
                f'<a class="flashcard-source" href="{e(reference["url"])}" '
                f'target="_blank" rel="noopener noreferrer">'
                f'{e(translations.translate("Read the MedlinePlus article ↗", language))}</a>'
            )
            topic_param = topic_value
        previous = (card_index - 1) % len(cards)
        next_card = (card_index + 1) % len(cards)
        card_html = f"""<section class="flashcard-panel"><div class="flashcard-progress"><span class="eyebrow">{e(progress)}</span><span>{e(category)}</span></div><div class="flashcard-front"><span class="eyebrow">QUESTION</span><h2>{e(flashcard_question)}</h2></div><details class="flashcard-reveal"><summary>Reveal answer</summary><div class="flashcard-back"><ul>{answer}</ul>{source_link}</div></details><nav class="flashcard-navigation" aria-label="Flashcard navigation"><a class="button button-outline" href="/study/flashcards?topic={quote_plus(topic_param)}&amp;card={previous}">← Previous</a><a class="button button-dark" href="/study/flashcards?topic={quote_plus(topic_param)}&amp;card={next_card}">Next card →</a></nav></section>"""
    elif topic_value:
        detail = (
            f'{translations.translate("No MedlinePlus article was found", language)}'
            f'{f": {reference_error}" if reference_error else ""}. '
            f'{translations.translate("No factual flashcards were generated.", language)}'
        )
        card_html = f"""<section class="content-panel flashcard-empty"><h2>No reviewed flashcards available</h2><p>{e(detail)}</p><a class="text-link" href="https://medlineplus.gov/" target="_blank" rel="noopener noreferrer">Search MedlinePlus ↗</a></section>"""
    content = f"""<section class="simple-hero"><a class="back-link" href="/study">← Study room</a><span class="eyebrow">ACTIVE RECALL</span><h1>Smart flashcards<span class="brand-period">.</span></h1><p>Choose any topic, try to recall the answer, then reveal it and move through the deck.</p></section>{picker}{save_control}{card_html}{notice("Learn safely.", "Cards summarize WellNote educational guides or linked MedlinePlus references. They are for study, not personal diagnosis or treatment.")}"""
    return layout("Smart flashcards", content, "study", language, current_url)


def body_verse_page(language="en", current_url="/"):
    def localized(text):
        return translations.translate(text, language)

    catalog = {}
    for layer in body_verse.LAYERS.values():
        for part in layer["parts"]:
            catalog[part["name"].casefold()] = {
                key: localized(part[key])
                for key in ("name", "system", "summary", "fact")
            }
    catalog_json = json.dumps(catalog, ensure_ascii=False).replace("<", "\\u003c")
    system_cards = []
    model_data = {}
    for system_id, system in body_verse.SYSTEMS.items():
        label = localized(system["label"])
        model_url = body_verse.MODEL_BASE_URL + quote(system["model"], safe="")
        model_data[system_id] = {
            "label": label,
            "description": localized(system["description"]),
            "model": model_url,
            "size": system["size"],
            "embed": system.get("embed"),
        }
        system_cards.append(
            f'<button type="button" class="anatomy-system-card" '
            f'data-system-card="{system_id}" aria-pressed="false">'
            f'<span class="anatomy-card-index">{len(system_cards) + 1:02}</span>'
            f'<span class="anatomy-card-name">{e(label)}</span>'
            f'<span class="anatomy-card-description">{e(localized(system["description"]))}</span>'
            f'<span class="anatomy-card-meta">{e(system["size"])} · {e(localized("loads when selected"))}</span>'
            f'</button>'
        )
    models_json = json.dumps(model_data, ensure_ascii=False).replace("<", "\\u003c")
    content = f"""<section class="simple-hero body-verse-hero"><a class="back-link" href="/study">{e(localized("← Study room"))}</a><span class="eyebrow">{e(localized("INTERACTIVE ANATOMY"))}</span><h1>Body Verse<span class="brand-period">.</span></h1><p>{e(localized("Explore the human body"))}</p></section>
    <section class="anatomy-systems" aria-label="{e(localized("Choose an anatomy system"))}">
      <div class="anatomy-section-heading"><div><span class="eyebrow">{e(localized("EXPLORE BY SYSTEM"))}</span><h2>{e(localized("Choose a body system"))}</h2></div><p>{e(localized("Choose a system to load its detailed 3D model. Models load on demand."))}</p></div>
      <div class="anatomy-system-grid">{"".join(system_cards)}</div>
    </section>
    <section class="body-verse-explorer" aria-label="{e(localized("Interactive anatomy explorer"))}">
      <div class="body-verse-main">
        <div class="body-verse-toolbar"><div><span class="eyebrow" data-viewer-system>{e(localized("3D ANATOMY VIEWER"))}</span><h2 data-viewer-title>{e(localized("Choose a system above"))}</h2></div></div>
        <div class="body-verse-stage" data-body-stage>
          <canvas class="body-verse-canvas" data-body-canvas aria-label="{e(localized("Interactive human body model"))}"></canvas>
          <div class="body-stage-empty" data-body-empty><span class="stage-orbit">↻</span><strong>{e(localized("Choose a system to begin"))}</strong><small>{e(localized("Drag to rotate · Scroll to zoom · Click a structure for details"))}</small></div>
          <div class="body-stage-loading" data-body-loading hidden><span class="anatomy-spinner"></span><strong data-loading-title>{e(localized("Preparing 3D anatomy"))}</strong><small data-loading-progress>{e(localized("Connecting to the model library…"))}</small></div>
          <div class="body-stage-error" data-body-error hidden role="alert"></div>
          <div class="body-stage-caption"><span class="stage-orbit">↻</span><span data-stage-instruction>{e(localized("Drag to rotate"))}<small>{e(localized("Click a structure to see its details"))}</small></span></div>
          <span class="stage-badge" data-stage-badge>{e(localized("Licensed 3D anatomy"))}</span>
        </div>
      </div>
      <aside class="body-verse-side-panel" aria-label="{e(localized("Selected anatomy details"))}">
        <div class="body-detail-card" aria-live="polite">
          <span class="eyebrow" data-detail-system>{e(localized("ANATOMY EXPLORER"))}</span>
          <h2 data-detail-name>{e(localized("No structure selected"))}</h2>
          <div class="body-detail-section"><span class="body-detail-icon">✳</span><div><h3>{e(localized("What it does"))}</h3><p data-detail-function>{e(localized("Select a structure in the 3D model or list to view its learning notes."))}</p></div></div>
          <div class="body-detail-fact"><span class="eyebrow">{e(localized("LEARN A LITTLE MORE"))}</span><p data-detail-fact>{e(localized("Notes are available for selected common structures; other model labels are shown with an introductory description and a trusted reference."))}</p><a class="body-detail-link" data-detail-link hidden target="_blank" rel="noopener noreferrer">{e(localized("Read a detailed reference"))} ↗</a></div>
        </div>
        <div class="body-part-navigation"><div class="anatomy-list-heading"><span class="eyebrow">{e(localized("MODEL STRUCTURES"))}</span><span data-structure-count>0</span></div><label class="anatomy-search-label" for="anatomy-search">{e(localized("Search this model"))}</label><input id="anatomy-search" class="anatomy-search" type="search" data-structure-search disabled placeholder="{e(localized("Choose a system first"))}"><p class="anatomy-list-empty" data-list-empty>{e(localized("Choose a system to load its structure list."))}</p><div class="body-part-list" data-structure-list role="list"></div><button type="button" class="anatomy-more-button" data-show-more hidden>{e(localized("Show more structures"))}</button></div>
      </aside>
    </section>
    <div class="body-model-credit"><strong>{e(localized("Model credit"))}:</strong> Z-Anatomy by Lluís Vinent Juanico and contributors; based on BodyParts3D by Database Center for Life Science. Licensed CC BY-SA 4.0 / CC BY-SA 2.1 Japan. <a href="https://github.com/LluisV/Z-Anatomy/blob/{body_verse.MODEL_REVISION}/Resources/Models/License.txt" target="_blank" rel="noopener noreferrer">{e(localized("View model credits and license"))} ↗</a></div>
    {notice("Anatomy for learning.", "The 3D atlas is an educational reference, not a complete clinical atlas. Structure notes are curated examples, not diagnosis or treatment advice.")}
    <script type="application/json" id="body-verse-models">{models_json}</script>
    <script type="application/json" id="body-verse-catalog">{catalog_json}</script>
    <script type="importmap">{{"imports":{{"three":"https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"}}}}</script>
    <script src="https://static.sketchfab.com/api/sketchfab-viewer-1.12.1.js" defer></script>
    <script type="module" src="/static/body-verse.js?v=20261124-original-sketchfab-ui"></script>"""
    return layout(
        "Body Verse",
        content,
        "study",
        language,
        current_url,
        extra_styles='<link rel="stylesheet" href="/static/body-verse.css">',
    )


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
    content = f"""<section class="simple-hero"><a class="back-link" href="/study">← Study room</a><span class="eyebrow">SIDE-BY-SIDE REVIEW</span><h1>Disease comparison<span class="brand-period">.</span></h1><p>Compare two health topics using reviewed WellNote guides or linked MedlinePlus references.</p></section>{picker}{results}{notice("Compare for learning, not diagnosis.", "Topics can differ in important ways beyond this summary. This comparison cannot determine what condition a person has or which treatment is right for them.")}"""
    return layout("Disease comparison", content, "study", language, current_url)


def research_decoder_page(
    abstract_input="",
    paper=None,
    sections=None,
    decode_error=None,
    ai_assisted=False,
    error=None,
    use_ai=False,
    followup_history=None,
    chat_state="",
    chat_error=None,
    chat_question="",
    followup_consent=False,
    language="en",
    current_url="/",
):
    import research_decoder

    followup_history = followup_history or []
    checked = " checked" if use_ai else ""
    form = f"""
        <form action="/study/research-decoder" method="post" class="research-form" id="research-decoder-form">
          <input type="hidden" name="action" value="decode">
          <label for="research-abstract">Paste your research abstract</label>
          <textarea id="research-abstract" name="abstract" rows="9" maxlength="{research_decoder.MAX_ABSTRACT_LENGTH}" required aria-describedby="research-counter research-input-help" placeholder="Copy your medical research abstract from PubMed or a scientific journal and paste it here...">{e(abstract_input)}</textarea>
          <div class="research-input-meta"><span id="research-counter" aria-live="polite">0 words · 0 / {research_decoder.MAX_ABSTRACT_LENGTH:,} characters</span><button class="research-clear" id="research-clear" type="button">Clear text</button></div>
          <p id="research-input-help">Paste abstract text only (up to {research_decoder.MAX_ABSTRACT_LENGTH:,} characters). Do not include personal or identifying health information.</p>
          <label class="research-consent"><input type="checkbox" name="use_ai" value="yes"{checked} required> I agree to send this abstract to the AI provider configured for WellNote so it can generate the explanation. The provider may process the text under its own terms.</label>
          <button class="button button-dark" type="submit" id="research-decode-button">Decode Abstract</button>
          <div class="research-loading" id="research-loading" role="status" aria-live="polite" hidden>
            <span class="research-spinner" aria-hidden="true"></span><span id="research-loading-message">Reading your research abstract...</span>
          </div>
        </form>
    """
    error_html = f'<p class="research-error" role="alert">{e(error)}</p>' if error else ""
    decode_error_html = (
        f'<p class="research-error" role="alert">{e(decode_error)}</p>'
        if decode_error else ""
    )

    def paragraph(text):
        return e(text).replace("\n", "<br>")

    paper_html = ""
    if paper:
        sections = sections or []
        token = ""
        download = ""
        chat_html = ""
        if sections:
            try:
                token = research_decoder.make_document_token(paper, sections)
                download = (
                    '<form action="/study/research-decoder" method="post" class="research-download">'
                    '<input type="hidden" name="action" value="download">'
                    f'<input type="hidden" name="document" value="{e(token)}">'
                    '<button class="button button-dark" type="submit">Download Decoded PDF</button>'
                    '<p class="research-download-status" role="status" aria-live="polite" hidden></p>'
                    '</form>'
                )
            except ValueError as exc:
                download = f'<p class="research-error" role="alert">PDF unavailable: {e(exc)}</p>'

            chat_state = chat_state or research_decoder.make_chat_token(followup_history)
            chat_turns = "".join(
                f'<article class="research-chat-turn"><div class="research-chat-question"><span>You asked</span><p>{paragraph(turn["question"])}</p></div>'
                f'<div class="research-chat-answer"><span>Study assistant</span><p>{paragraph(turn["answer"])}</p></div></article>'
                for turn in followup_history
            )
            chat_error_html = (
                f'<p class="research-error" role="alert">{e(chat_error)}</p>'
                if chat_error else ""
            )
            chat_html = (
                '<section class="research-chat"><div class="research-chat-heading"><span class="eyebrow">KEEP LEARNING</span>'
                '<h3>Ask Questions About This Research</h3><p>Ask about the study design, results, terminology, limitations, or exam takeaways. Answers use the pasted abstract and this decoded document.</p></div>'
                f'<div class="research-chat-history">{chat_turns}</div>{chat_error_html}'
                '<form action="/study/research-decoder" method="post" class="research-followup-form">'
                '<input type="hidden" name="action" value="followup">'
                f'<input type="hidden" name="document" value="{e(token)}">'
                f'<input type="hidden" name="chat_state" value="{e(chat_state)}">'
                f'<label for="research-question">Your question</label><textarea id="research-question" name="question" rows="3" maxlength="{research_decoder.MAX_CHAT_QUESTION_LENGTH}" required placeholder="For example: What does the confidence interval tell me?">{e(chat_question)}</textarea>'
                f'<label class="research-consent"><input type="checkbox" name="followup_ai_consent" value="yes"{" checked" if followup_consent else ""} required> I agree to send this question, the abstract, and decoded sections to the configured AI provider.</label>'
                '<button class="button button-outline" type="submit">Ask about this research</button></form>'
                '</section>'
            )
        paper_html = (
            '<article class="research-paper"><header class="research-paper-header">'
            '<span class="eyebrow">YOUR ABSTRACT · EDUCATIONAL STUDY AID</span>'
            '<h2>Your decoded research is ready</h2>'
            '<p class="research-citation">Download the study document or ask a question about this abstract.</p>'
            f'<div class="research-document-actions">{download}</div></header>'
            f'{decode_error_html}'
            f'{chat_html}'
            '</article>'
        )

    content = (
        '<section class="simple-hero research-hero"><a class="back-link" href="/study">← Study room</a>'
        '<span class="eyebrow">UNDERSTAND RESEARCH · LEARN SMARTER</span>'
        '<h1>Research Decoder<span class="brand-period">.</span></h1>'
        '<p>Understand research papers. Decode medical science. Learn smarter.</p></section>'
        f'{form}{error_html}{paper_html}'
        f'{notice("Educational research learning, not medical advice.", "AI explanations may be wrong and abstracts may omit important context. Verify claims against the original paper; this tool does not diagnose, recommend treatment, or analyze the full paper.")}'
    )
    return layout(
        "Research decoder", content, "study", language, current_url,
        '<link rel="stylesheet" href="/static/research-decoder.css"><script src="/static/research-decoder.js" defer></script>',
    )


def study_page(diseases, greeting, response=None, question=None, selected=None, result=None, prompt=None, language="en", current_url="/"):
    import study

    diseases = [translations.localize_disease(item, language) for item in diseases]
    question = translations.localize_question(question, language) if question else None
    selected = translations.localize_disease(selected, language) if selected else None
    provider_note = (
        "A model provider is configured; its answers may be incomplete or incorrect. "
        "For personal medical concerns, consult a qualified health professional."
        if study.ai_provider_configured()
        else
        "No AI model is configured in this app, so replies use curated local study "
        "content. To use Gemini, set GEMINI_API_KEY; the default model is "
        "gemini-3.5-flash-lite. For other providers, see README.md. For personal medical "
        "concerns, consult a qualified health professional."
    )
    lesson_cards = "".join(
        f'<a class="study-card" href="/study/{quote(item["slug"], safe="")}"><span class="study-card-icon">✎</span><span><small>{e(item["category"])}</small><strong>{e(item["name"])}</strong><em>{e(translations.translate("Review key points →", language))}</em></span></a>'
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
    voice_privacy_note = (
        f'<p class="scope-note">{e(translations.translate("If no matching device voice is installed, Read aloud sends the reply text to Google Gemini to create audio.", language))}</p>'
        if study.gemini_speech_configured() else ""
    )
    bot = f"""<section class="tutor-card"><div class="tutor-heading"><span class="bot-avatar">✳</span><div><strong>Your study buddy</strong><small>Ready when you are</small></div><span class="online-dot"></span></div><div class="chat-bubble"><p>{e(greeting)}</p></div>{user_message}{response_html}<p class="tutor-hint">Try: “Help me plan for NEET”, “Explain biology”, “Help with homework”, or “Give me a study strategy.”</p><form action="/study/ask" method="post" class="prompt-form"><label class="sr-only" for="study-prompt">Ask a study question</label><textarea id="study-prompt" name="prompt" rows="3" placeholder="Ask a study question…"></textarea><button class="button button-dark" type="submit">Send <span>→</span></button></form>{voice_tools}{voice_privacy_note}<p class="scope-note">{e(provider_note)}</p><p class="scope-note">Confirm exam requirements with official sources.</p>{exam_links}</section>"""
    if selected:
        intro = f'<section class="simple-hero"><a class="back-link" href="/study">← Study room</a><span class="eyebrow">{e(translations.translate("FOCUSED REVIEW", language))} · {e(selected["category"])}</span><h1>{e(selected["name"])}<span class="brand-period">.</span></h1><p>Take a moment with the essentials, then revisit the full guide when you’re ready.</p></section>'
        points = "".join(f'<li class="study-point"><span class="point-number">{index:02d}</span><p>{e(point)}</p></li>' for index, point in enumerate(selected["study_points"], 1))
        main = f'<section class="study-content"><div class="study-notebook"><span class="eyebrow">THREE THINGS TO REMEMBER</span><ol class="study-points">{points}</ol><a class="button button-dark" href="/disease/{quote(selected["slug"], safe="")}">Read the full guide →</a> <a class="button button-outline" href="/study/mind-map?topic={quote(selected["slug"], safe="")}">Make a mind map</a> <a class="button button-outline" href="/study/flashcards?topic={quote(selected["slug"], safe="")}">Study with flashcards</a> <a class="button button-outline" href="/study/compare?first={quote_plus(selected["name"])}">Compare with another topic</a></div><aside class="reflection-card"><span class="reflection-icon">✳</span><span class="eyebrow">REFLECT</span><h2>What would you like to ask a health professional?</h2><p>Use what you’ve learned to prepare questions for a conversation about your own health.</p></aside></section>'
        content = intro + main + bot + notice("Keep learning in context.", "Study notes summarize educational topics; they are not diagnostic tools or personal care recommendations.")
    elif question:
        options = "".join(f'<label class="answer-option"><input type="radio" name="answer" value="{i}" required>{"ABCD"[i]}. {e(option)}</label>' for i, option in enumerate(question["options"]))
        feedback = f'<div class="answer-feedback {"correct" if result == question["answer"] else "incorrect"}"><strong>{"Correct!" if result == question["answer"] else "Not quite—review the explanation."}</strong><p>{e(question["explanation"])}</p></div>' if result is not None else ""
        practice_label = translations.translate("ORIGINAL PRACTICE", language)
        question_form = f'<div class="quiz-card"><span class="eyebrow">{e(question["subject"])} · {e(practice_label)}</span><h2>{e(question["question"])}</h2><form action="/study/answer/{e(question["id"])}" method="post" class="answer-form">{options}<button class="button button-dark" type="submit">Check answer</button></form>{feedback}<a class="button button-outline next-question" href="/study/question?after={quote(question["id"], safe="")}">Next question →</a></div>'
        content = f'<section class="simple-hero"><span class="eyebrow">PRACTICE, AT YOUR PACE</span><h1>One question at a time<span class="brand-period">.</span></h1><p>Original introductory examples. Check your reasoning with each explanation.</p></section><section class="practice-layout">{question_form}{bot}</section>{notice("Original practice only.", "These introductory questions are not official NEET, MCAT, or AAMC exam items and do not represent the full syllabus.")}'
    else:
        intro = '<section class="study-intro"><div><span class="eyebrow">A GENTLER WAY TO LEARN</span><h1>Welcome to your<br><span>study room.</span></h1><p>Short reviews, original practice, and a small study companion—no pressure, just a little more understanding.</p><div class="study-actions"><a class="button button-dark" href="/study/question">Try a practice question →</a><a class="button button-outline" href="/study/textbooks">Open textbook library →</a><a class="button button-outline" href="/study/body-verse">Explore Body Verse →</a><a class="button button-outline" href="/study/mind-map">Generate a mind map</a><a class="button button-outline" href="/study/flashcards">Smart flashcards</a><a class="button button-outline" href="/study/compare">Compare diseases</a><a class="button button-outline" href="/study/research-decoder">Research decoder</a></div></div><div class="study-illustration" aria-hidden="true"><span class="study-plant">✳</span><span class="study-book">✎</span><span class="study-underline"></span></div></section>'
        main = f'<section class="study-content study-home"><div><div class="section-heading"><div><span class="eyebrow">YOUR TOPICS</span><h2>Choose what to review</h2><p>Essentials from each health guide.</p></div></div><div class="study-grid">{lesson_cards}</div><div class="exam-panel"><span class="eyebrow">EXAM STARTERS</span><h2>Preparing for an exam?</h2><p>Ask the study buddy about NEET, MCAT, or AAMC. For current exam details and syllabi, check the official provider.</p>{exam_links}</div></div>{bot}</section>{notice("Study, not a substitute.", "Study buddy replies are for education, not personal diagnosis or treatment. For your own symptoms or care, consult a qualified health professional.")}'
        content = intro + main
    content += '<script src="/static/voice-tutor.js" defer></script>'
    return layout("Study room", content, "study", language, current_url)


def error_page(title, message, status="404 Not Found", language="en", current_url="/"):
    body = f'<section class="simple-hero"><span class="eyebrow">OOPS</span><h1>{e(title)}<span class="brand-period">.</span></h1><p>{e(message)}</p><a class="button button-dark" href="/">Back to explore →</a></section>'
    return status, layout(title, body, language=language, current_url=current_url)


def textbook_progress(book, state):
    completed = sum(
        (book["id"], chapter["id"]) in state["completed"]
        for chapter in book["chapters"]
    )
    total = len(book["chapters"])
    return completed, total, round(completed * 100 / total) if total else 0


def textbook_metadata(book):
    return (
        '<dl class="textbook-metadata">'
        f'<div><dt>Senior contributing authors</dt><dd>{e(book["authors"])}</dd></div>'
        f'<div><dt>Publisher</dt><dd>{e(book["publisher"])}</dd></div>'
        f'<div><dt>License</dt><dd><a href="{e(book["license_url"])}" target="_blank" rel="noopener noreferrer">{e(book["license"])}</a></dd></div>'
        f'<div><dt>Official source</dt><dd><a href="{e(book["source"])}" target="_blank" rel="noopener noreferrer">OpenStax book page ↗</a></dd></div>'
        "</dl>"
    )


def textbook_chapter_link(book, chapter, label=None):
    title = label or f'Chapter {chapter["number"]}: {chapter["title"]}'
    return (
        f'<a href="/study/textbooks/{e(book["id"])}/{e(chapter["id"])}">'
        f'{e(title)}</a>'
    )


def openstax_subject_links():
    labels = {
        "Physics": "Physics",
        "Chemistry": "Chemistry",
        "Biology": "Biology",
        "Others": "Others · Anatomy and Physiology",
    }
    return (
        '<nav class="openstax-subject-links" aria-label="OpenStax subject catalogs">'
        '<span>Official subject catalogs</span>'
        + "".join(
            f'<a href="{e(openstax.FIELD_URLS[field])}" target="_blank" rel="noopener noreferrer">{e(labels[field])} ↗</a>'
            for field in openstax.ALLOWED_FIELDS
        )
        + "</nav>"
    )


def textbook_library_page(books, state, query="", subject="", level="", language="en", current_url="/"):
    subjects = sorted({book["subject"] for book in books})
    levels = sorted({book["level"] for book in books})
    query_folded = query.casefold()
    matches = [
        book for book in books
        if (not subject or book["subject"] == subject)
        and (not level or book["level"] == level)
        and (not query_folded or query_folded in " ".join(
            (book["title"], book["subject"], book["level"], book["authors"], book["audience"])
        ).casefold())
    ]
    subject_options = '<option value="">All subjects</option>' + "".join(
        f'<option value="{e(value)}"{" selected" if value == subject else ""}>{e(value)}</option>'
        for value in subjects
    )
    level_options = '<option value="">All levels</option>' + "".join(
        f'<option value="{e(value)}"{" selected" if value == level else ""}>{e(value)}</option>'
        for value in levels
    )
    cards = []
    for book in matches:
        completed, total, percent = textbook_progress(book, state)
        cards.append(
            f'<article class="textbook-card"><div class="textbook-card-top"><span class="eyebrow">{e(book["subject"])}</span><span class="textbook-level">{e(book["level"])}</span></div>'
            f'<h2><a href="/study/textbooks/{e(book["id"])}">{e(book["title"])}</a></h2>'
            f'<p class="textbook-audience">{e(book["audience"])}</p>'
            f'<p class="textbook-byline"><strong>Senior contributing authors</strong> {e(book["authors"])}</p>'
            f'<p class="textbook-byline"><strong>Publisher</strong> {e(book["publisher"])}</p>'
            f'<p class="textbook-license"><a href="{e(book["license_url"])}" target="_blank" rel="noopener noreferrer">{e(book["license"])}</a></p>'
            f'<p class="textbook-byline"><strong>Official source</strong> <a href="{e(book["source"])}" target="_blank" rel="noopener noreferrer">OpenStax ↗</a></p>'
            f'<div class="textbook-progress"><div><span>Reading progress</span><strong>{completed}/{total} selected chapters · {percent}%</strong></div><progress value="{percent}" max="100">{percent}%</progress></div>'
            f'<a class="button button-dark" href="/study/textbooks/{e(book["id"])}">Browse chapters →</a></article>'
        )
    if not cards:
        cards.append('<div class="empty-state"><h2>No titles match those filters</h2><p>Try a different subject, level, or search.</p></div>')
    bookmarked = []
    for book in books:
        for chapter in book["chapters"]:
            if (book["id"], chapter["id"]) in state["bookmarks"]:
                bookmarked.append(
                    f'<li>{textbook_chapter_link(book, chapter)} <span>{e(book["title"])}</span></li>'
                )
    bookmark_section = (
        '<section class="textbook-bookmarks"><span class="eyebrow">YOUR BOOKMARKS</span><h2>Return to a saved chapter</h2><ul>'
        + "".join(bookmarked) + "</ul></section>"
        if bookmarked else ""
    )
    content = (
        '<section class="simple-hero textbook-hero"><a class="back-link" href="/study">← Study room</a>'
        '<span class="eyebrow">OPEN HEALTH TEXTBOOKS</span><h1>A library for learning<span class="brand-period">.</span></h1>'
        '<p>Browse selected open textbooks by subject and level. The complete books stay with their publishers; WellNote links to official chapters and adds original study aids.</p></section>'
        '<form class="openstax-search-form" action="/study/textbooks/search" method="get">'
        '<label for="openstax-query">Search all OpenStax book titles</label>'
        '<div><input id="openstax-query" type="search" name="q" placeholder="Try biology, chemistry, physics, or MCAT" required>'
        '<select name="field" aria-label="Limit results by field"><option value="">All allowed fields</option>'
        '<option value="Physics">Physics</option><option value="Chemistry">Chemistry</option>'
        '<option value="Biology">Biology</option><option value="Others">Others · Anatomy and Physiology</option></select>'
        '<button class="button button-dark" type="submit">Search OpenStax</button></div>'
        '<small>Searches the live catalog; results are limited to medical foundations in Physics, Chemistry, Biology, and Anatomy and Physiology.</small></form>'
        f'{openstax_subject_links()}'
        '<form class="textbook-filters" action="/study/textbooks" method="get">'
        f'<label>Filter curated titles<input type="search" name="q" value="{e(query)}" placeholder="Try anatomy or infection"></label>'
        f'<label>Subject<select name="subject">{subject_options}</select></label>'
        f'<label>Level<select name="level">{level_options}</select></label>'
        '<button class="button button-outline" type="submit">Filter library</button></form>'
        f'<section class="textbook-grid" aria-label="Textbook titles">{"".join(cards)}</section>'
        f'{bookmark_section}'
        f'{notice("Educational use only.", "Textbook links and original WellNote learning aids support study; they are not medical advice. Confirm clinical questions with qualified professionals.")}'
    )
    return layout(
        "Textbook library", content, "study", language, current_url,
        '<link rel="stylesheet" href="/static/textbooks.css">',
    )


def openstax_search_page(query, field, results, error=None, language="en", current_url="/"):
    field_labels = {
        "Physics": "Physics",
        "Chemistry": "Chemistry",
        "Biology": "Biology",
        "Others": "Others · Anatomy and Physiology",
    }
    field_options = '<option value="">All allowed fields</option>' + "".join(
        f'<option value="{name}"{" selected" if field == name else ""}>{e(field_labels[name])}</option>'
        for name in openstax.ALLOWED_FIELDS
    )
    cards = "".join(
        f'<article class="openstax-result"><span class="eyebrow">{e(book["field"])} · MEDICAL FOUNDATION</span>'
        f'<h2><a href="{e(book["url"])}" target="_blank" rel="noopener noreferrer">{e(book["title"])}</a></h2>'
        f'<p>Official OpenStax listing · {e(book["field"])}</p>'
        f'<a class="text-link" href="{e(book["url"])}" target="_blank" rel="noopener noreferrer">Open book at OpenStax ↗</a>'
        f'<a class="text-link openstax-subject-link" href="{e(book["subject_url"])}" target="_blank" rel="noopener noreferrer">Browse {e(field_labels[book["field"]])} ↗</a></article>'
        for book in results
    )
    if error:
        result_content = (
            f'<div class="openstax-empty"><strong>OpenStax search is unavailable.</strong><p>{e(error)}</p>'
            '<a href="/study/textbooks">Return to the curated library</a></div>'
        )
    elif query and not results:
        result_content = (
            '<div class="openstax-empty"><strong>No such content available.</strong>'
            '<p>No live OpenStax title matched that search within the medical-related Physics, Chemistry, Biology, or Anatomy and Physiology fields.</p>'
            '<a href="/study/textbooks">Browse the curated library</a></div>'
        )
    elif not query:
        result_content = (
            '<div class="openstax-empty"><strong>Search the OpenStax catalog.</strong>'
            '<p>Enter a title, subject, or medical entrance exam term to find matching books.</p></div>'
        )
    else:
        result_content = f'<section class="openstax-results" aria-label="OpenStax results">{cards}</section>'
    content = (
        '<section class="simple-hero textbook-hero"><a class="back-link" href="/study/textbooks">← Textbook library</a>'
        '<span class="eyebrow">LIVE OPENSTAX CATALOG</span><h1>Search medical foundations<span class="brand-period">.</span></h1>'
        '<p>Search book titles across the OpenStax catalog. WellNote displays only books classified under Physics, Chemistry, Biology, or Anatomy and Physiology for medical and entrance-exam foundations.</p></section>'
        '<form class="openstax-search-form" action="/study/textbooks/search" method="get">'
        f'<label for="openstax-query">Search all OpenStax book titles</label><div><input id="openstax-query" type="search" name="q" value="{e(query)}" placeholder="Try biology, chemistry, physics, or MCAT" required>'
        f'<select name="field" aria-label="Limit results by field">{field_options}</select>'
        '<button class="button button-dark" type="submit">Search OpenStax</button></div>'
        '<small>Only live catalog entries in the allowed medical-foundation subject fields are included. Full text remains on OpenStax.</small></form>'
        f'{openstax_subject_links()}'
        f'{result_content}'
        f'{notice("Catalog search, not a medical reference.", "Search results link to official OpenStax book pages. They are educational resources, not medical advice or a substitute for clinical training.")}'
    )
    return layout(
        "Search OpenStax", content, "study", language, current_url,
        '<link rel="stylesheet" href="/static/textbooks.css">',
    )


def textbook_book_page(book, state, query="", language="en", current_url="/"):
    query_folded = query.casefold()
    chapters = [
        chapter for chapter in book["chapters"]
        if not query_folded or query_folded in " ".join((
            chapter["title"], chapter["summary"], chapter["keywords"],
            " ".join(term for term, _ in chapter["glossary"]),
        )).casefold()
    ]
    rows = "".join(
        f'<li class="textbook-chapter-row"><div><span class="eyebrow">CHAPTER {chapter["number"]:02d}</span>'
        f'<h2>{textbook_chapter_link(book, chapter)}</h2><p>{e(chapter["summary"])}</p></div>'
        f'<a class="text-link" href="{e(book["source"] + "/pages/" + chapter["source_slug"])}" target="_blank" rel="noopener noreferrer">Official chapter ↗</a></li>'
        for chapter in chapters
    ) or '<li class="empty-state"><p>No chapters match that search.</p></li>'
    completed, total, percent = textbook_progress(book, state)
    content = (
        f'<section class="simple-hero textbook-hero"><a class="back-link" href="/study/textbooks">← Textbook library</a>'
        f'<span class="eyebrow">{e(book["subject"])} · {e(book["level"])}</span><h1>{e(book["title"])}<span class="brand-period">.</span></h1>'
        f'<p>{e(book["audience"])}</p></section>'
        f'<section class="textbook-detail-layout"><div><div class="textbook-book-progress"><span>Reading progress</span><strong>{completed} of {total} selected chapters · {percent}%</strong><progress value="{percent}" max="100">{percent}%</progress></div>'
        f'<form class="textbook-search" action="/study/textbooks/{e(book["id"])}" method="get"><label for="chapter-search">Search this book’s chapter list</label><div><input id="chapter-search" type="search" name="q" value="{e(query)}" placeholder="Search chapters, summaries, or terms"><button class="button button-dark" type="submit">Search</button></div></form>'
        f'<div class="textbook-chapter-heading"><span class="eyebrow">SELECTED CHAPTERS</span><span>Open official source for full text</span></div><ol class="textbook-chapters">{"".join(rows)}</ol></div>'
        f'<aside class="textbook-source-card"><span class="eyebrow">BOOK DETAILS</span>{textbook_metadata(book)}'
        f'<p>{e(book["source_note"])}</p><p><strong>Attribution</strong><br>{e(book["attribution"])}</p></aside></section>'
        f'{notice("A link-out reader, not a copy.", "WellNote does not reproduce the book. Chapter notes, terms, and self-check questions here are original WellNote material; consult the linked text for the complete chapter.")}'
    )
    return layout(
        book["title"], content, "study", language, current_url,
        '<link rel="stylesheet" href="/static/textbooks.css">',
    )


def textbook_reader_page(book, chapter, state, font_size="medium", query="", language="en", current_url="/"):
    key = (book["id"], chapter["id"])
    bookmarked = key in state["bookmarks"]
    completed = key in state["completed"]
    chapter_url = f'{book["source"]}/pages/{chapter["source_slug"]}'
    search_folded = query.casefold()
    search_results = [
        item for item in book["chapters"]
        if search_folded and search_folded in " ".join((
            item["title"], item["summary"], item["keywords"],
            " ".join(term + " " + definition for term, definition in item["glossary"]),
        )).casefold()
    ]
    search_html = ""
    if query:
        results = "".join(
            f'<li>{textbook_chapter_link(book, item)} <span>Chapter {item["number"]}</span></li>'
            for item in search_results
        ) or "<li>No matching selected chapters.</li>"
        search_html = (
            f'<section class="textbook-search-results"><strong>Search results for “{e(query)}”</strong><ul>{results}</ul></section>'
        )
    glossary = "".join(
        f'<dt>{e(term)}</dt><dd>{e(definition)}</dd>'
        for term, definition in chapter["glossary"]
    )
    review = "".join(
        f'<li><h3>{e(item["question"])}</h3><details><summary>Reveal a sample answer</summary><p>{e(item["answer"])}</p></details></li>'
        for item in chapter["review"]
    )
    font_links = ""
    for size, label in (("small", "A−"), ("medium", "A"), ("large", "A+")):
        selected = size == font_size
        current_attribute = ' aria-current="true"' if selected else ""
        font_links += (
            f'<a class="font-choice{" selected" if selected else ""}" '
            f'href="/study/textbooks/{e(book["id"])}/{e(chapter["id"])}?font={size}"'
            f'{current_attribute}>{label}</a>'
        )
    completed_label = "Mark as unread" if completed else "Mark chapter complete"
    bookmark_label = "Remove bookmark" if bookmarked else "Bookmark chapter"
    completed_count, total, percent = textbook_progress(book, state)
    content = (
        f'<section class="simple-hero textbook-hero"><a class="back-link" href="/study/textbooks/{e(book["id"])}">← {e(book["title"])}</a>'
        f'<span class="eyebrow">CHAPTER {chapter["number"]:02d} · {e(book["subject"])}</span><h1>{e(chapter["title"])}<span class="brand-period">.</span></h1>'
        f'<p>Original WellNote review notes, paired with the complete chapter at its official source.</p></section>'
        f'<div class="textbook-reader-toolbar"><form class="textbook-search" action="/study/textbooks/{e(book["id"])}" method="get"><label for="reader-search">Search this book</label><div><input id="reader-search" type="search" name="q" value="{e(query)}" placeholder="Search chapter titles and learning notes"><button class="button button-dark" type="submit">Search</button></div></form>'
        f'<div class="font-controls" aria-label="Reading text size"><span>Text size</span>{font_links}</div></div>{search_html}'
        f'<div class="textbook-reader-layout"><article class="textbook-reading-pane {e(font_size)}">'
        f'<section><span class="eyebrow">QUICK SUMMARY</span><p class="textbook-summary">{e(chapter["summary"])}</p></section>'
        f'<section><span class="eyebrow">GLOSSARY</span><dl class="textbook-glossary">{glossary}</dl></section>'
        f'<section><span class="eyebrow">REVIEW QUESTIONS</span><ol class="textbook-review">{review}</ol></section>'
        f'<p class="textbook-original-note">These notes and questions are original WellNote learning aids, not copied from the textbook.</p>'
        f'<a class="button button-dark official-chapter-link" href="{e(chapter_url)}" target="_blank" rel="noopener noreferrer">Read full chapter at OpenStax ↗</a></article>'
        f'<aside class="textbook-reader-aside"><div class="textbook-book-progress"><span>Book progress</span><strong>{completed_count}/{total} selected chapters · {percent}%</strong><progress value="{percent}" max="100">{percent}%</progress></div>'
        f'<form class="textbook-state-form" action="/study/textbooks/state" method="post"><input type="hidden" name="book" value="{e(book["id"])}"><input type="hidden" name="chapter" value="{e(chapter["id"])}"><input type="hidden" name="action" value="bookmark"><button class="button button-outline" type="submit">{"★" if bookmarked else "☆"} {bookmark_label}</button></form>'
        f'<form class="textbook-state-form" action="/study/textbooks/state" method="post"><input type="hidden" name="book" value="{e(book["id"])}"><input type="hidden" name="chapter" value="{e(chapter["id"])}"><input type="hidden" name="action" value="complete"><button class="button button-outline" type="submit">{"✓" if completed else "○"} {completed_label}</button></form>'
        f'<div class="textbook-source-card"><span class="eyebrow">SOURCE & LICENSE</span><p><strong>{e(book["title"])}</strong><br>{e(book["authors"])}</p><p>{e(book["publisher"])}</p><p><a href="{e(book["license_url"])}" target="_blank" rel="noopener noreferrer">{e(book["license"])}</a></p><p><a href="{e(chapter_url)}" target="_blank" rel="noopener noreferrer">Official chapter ↗</a></p></div></aside></div>'
        f'{notice("Educational material only.", "WellNote summaries and questions are for learning, not diagnosis or treatment. Always consult a qualified health professional for personal medical concerns.")}'
    )
    return layout(
        chapter["title"], content, "study", language, current_url,
        '<link rel="stylesheet" href="/static/textbooks.css">',
    )
