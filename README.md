# WellNote

WellNote is a small, server-rendered medical learning app built with Python's
standard library. Application logic, disease search, saved topics, study prompts,
and practice-question checking run in Python; pages use HTML forms and CSS.
Browser scripts are reserved for browser-only speech features and the WebGL
anatomy renderer; app routes, study behavior, and educational content remain
server-side Python. No third-party Python packages are required. The study buddy can connect
to a configurable OpenAI-compatible chat-completions API for general conversation
and study help.

## Run locally

Use Python 3.9 or newer:

```text
python app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Run the tests with:

```text
python -m unittest
```

For hosting platforms, WellNote binds to `0.0.0.0` and reads the listening
port from the `PORT` environment variable. If `PORT` is unset, it uses `8000`,
so the local command above remains unchanged.

## Configure generative study-buddy answers

The app does not bundle an AI model or API key. Without provider credentials,
the study buddy uses its curated local education answers and references. To
enable general model-generated replies with Gemini, set `GEMINI_API_KEY` and
restart the app. It uses Gemini's OpenAI-compatible chat-completions endpoint
and defaults to `gemini-2.5-flash`; optionally set `GEMINI_MODEL` to select
another available Gemini model. The key is read from the environment and must
not be committed to the repository.

PowerShell:

```powershell
$env:GEMINI_API_KEY = "your-gemini-api-key"
# Optional model overrides:
$env:GEMINI_MODEL = "gemini-2.5-flash"
$env:GEMINI_TTS_MODEL = "gemini-3.8-flash-tts"
python app.py
```

POSIX shell:

```sh
export GEMINI_API_KEY="your-gemini-api-key"
export GEMINI_MODEL="gemini-2.5-flash"
export GEMINI_TTS_MODEL="gemini-3.8-flash-tts"
python app.py
```

For another OpenAI-compatible provider, configure `WELLNOTE_AI_API_KEY`,
`WELLNOTE_AI_MODEL`, and optionally `WELLNOTE_AI_BASE_URL`:

```powershell
$env:WELLNOTE_AI_API_KEY = "your-provider-key"
$env:WELLNOTE_AI_MODEL = "your-model-name"
$env:WELLNOTE_AI_BASE_URL = "https://your-provider.example/v1"
python app.py
```

```sh
export WELLNOTE_AI_API_KEY="your-provider-key"
export WELLNOTE_AI_MODEL="your-model-name"
export WELLNOTE_AI_BASE_URL="https://your-provider.example/v1"
python app.py
```

`WELLNOTE_AI_BASE_URL` defaults to `https://api.openai.com/v1`. The model's
knowledge and reliability depend on the configured provider and model; answers
can be incomplete or incorrect. WellNote does not guarantee comprehensive
world knowledge. Provider errors are shown in the study buddy instead of being
silently replaced with a canned answer.

The study room's read-aloud controls use the browser's speech-synthesis feature
and select a voice matching the current language. Hindi and Hinglish playback uses a matching installed device voice when
available. If no matching voice exists and `GEMINI_API_KEY` is configured,
WellNote can generate audio with Gemini TTS (`GEMINI_TTS_MODEL`, default
`gemini-3.8-flash-tts`) instead of silently using an English voice. In that
fallback, the study-buddy reply text is sent to Google's Gemini API to create
audio. Hinglish playback converts common Romanized Hindi words to Devanagari
for clearer pronunciation. Tutor questions are entered as text.

## What's included

- Searchable disease guides with descriptions, common symptoms, prevention,
  treatment context, and a link to a health authority.
- Searches outside the curated guides use the U.S. National Library of
  Medicine's MedlinePlus health-topics API and show linked, source-attributed
  summaries. If the reference service is unavailable or has no result, the app
  says so and offers MedlinePlus directly instead of inventing details.
- A reading list for reviewed guides and typed MedlinePlus topics, stored in a
  browser cookie.
- A study room with rotating greetings, a configurable AI study companion (or
  curated local replies when no AI provider is configured), and spoken answers
  through browser speech features,
  introductory original practice questions, and answer explanations.
- A textbook portal inside the Study Room with curated OpenStax Anatomy and
  Physiology 2e and Microbiology titles, subject/level filters, official chapter
  links, in-book chapter search, adjustable reading size, browser-cookie
  bookmarks and chapter completion progress, plus original WellNote summaries,
  glossary terms, and self-check questions. It also searches the live OpenStax
  catalog and displays only medical-foundation books in Physics, Chemistry,
  Biology, and “Others” (Anatomy and Physiology), with links to each official
  OpenStax subject page. Each curated title displays its authors, publisher,
  source, and verified CC BY-NC-SA 4.0 license.
- A study-buddy overview of all 13 essential vitamins, common deficiency
  findings, dietary sources, a link to NIH fact sheets, and clinical safety context.
- A mind map generator that accepts any typed health topic. It uses WellNote's
  reviewed guides when available, otherwise searches MedlinePlus; missing
  details are labeled as unavailable, with links to the full article for details.
- Smart flashcards generated from reviewed local guides or MedlinePlus summaries,
  with revealable answers and URL-based next/previous navigation.
- Side-by-side comparison for two typed health topics, using reviewed WellNote
  guides or MedlinePlus references and marking unavailable details clearly.
- Body Verse, a WebGL anatomy viewer with system cards, mouse/touch rotate and
  zoom, searchable/selectable model structures, and a details panel. It loads
  licensed Z-Anatomy FBX models on demand; reviewed notes are shown where
  available, while uncatalogued structures are identified without invented
  descriptions. The skeleton is the final system card.
- An English/Hindi/Hinglish language switcher. The interface, reviewed starter
  guides, and built-in practice questions are available in Hindi and
  Roman-script Hinglish. MedlinePlus excerpts retain their source wording;
  configured study-buddy models are asked to answer in the selected language,
  though external and local fallback replies may not be fully translated.
- NEET, MCAT, and AAMC study prompts that point learners toward official
  information; the app does not reproduce official exam questions.
- Responsive styling, accessible form labels, and medical-learning disclaimers.

## Scope and safety

The built-in disease library and local tutor provide curated educational
examples—not an exhaustive database, a diagnostic system, or a full exam
preparation course. Generative answers require the optional configured provider
and are not guaranteed complete or correct.
The textbook portal links to publishers' official pages and does not reproduce
their chapters. Its short summaries, glossary entries, and self-check questions
are original WellNote learning aids. OpenStax books have title-specific terms;
the listed titles are licensed CC BY-NC-SA 4.0, so review the linked license
before reusing or adapting any source material. Live OpenStax search reads its
public book-catalog metadata and links to official book pages; it does not fetch
or display full chapter text and excludes subjects outside Physics, Chemistry,
Biology, and Anatomy and Physiology.
Body Verse requires WebGL and an internet connection to load Three.js and the
selected 3D anatomy model. Depending on the selected system, the source model
download is approximately 2–65 MB. The models are from [Z-Anatomy](https://github.com/LluisV/Z-Anatomy)
and [BodyParts3D](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html)
and are attributed in the viewer under their applicable Creative Commons
licenses; see the linked upstream model credits for additional contributors and
license details.
Unknown disease searches use the external
MedlinePlus service and require an internet connection; it may not have an
article for every topic. Medical information is for general education and is
not personal medical advice. For
symptoms, diagnosis, or treatment, consult a qualified health professional; for
a possible emergency, contact local emergency services. Confirm exam syllabi and
rules with the relevant official exam provider.

To extend the app, add reviewed disease entries and their references to
`diseases.py`, or original, checked practice questions to `study.py`.
