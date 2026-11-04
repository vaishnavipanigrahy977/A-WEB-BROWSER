# Wellnote

Wellnote is a small, server-rendered medical learning app built with Python's
standard library. Application logic, disease search, saved topics, study prompts,
and practice-question checking run in Python; pages use HTML forms and CSS rather
than JavaScript application code or third-party packages. The study buddy can
connect to a configurable OpenAI-compatible chat-completions API for general
conversation and study help.

## Run locally

Use Python 3.9 or newer:

```text
python app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Run the tests with:

```text
python -m unittest
```

For hosting platforms, Wellnote binds to `0.0.0.0` and reads the listening
port from the `PORT` environment variable. If `PORT` is unset, it uses `8000`,
so the local command above remains unchanged.

## Configure generative study-buddy answers

The app does not bundle an AI model or API key. Without provider credentials,
the study buddy uses its curated local education answers and references. To
enable general model-generated replies, configure a provider that implements
the OpenAI-compatible `POST /v1/chat/completions` API, then restart the app.
The key is read from the environment and must not be committed to the repository.

PowerShell:

```powershell
$env:WELLNOTE_AI_API_KEY = "your-provider-key"
$env:WELLNOTE_AI_MODEL = "your-model-name"
# Optional for a compatible provider other than the default endpoint:
$env:WELLNOTE_AI_BASE_URL = "https://your-provider.example/v1"
python app.py
```

POSIX shell:

```sh
export WELLNOTE_AI_API_KEY="your-provider-key"
export WELLNOTE_AI_MODEL="your-model-name"
# Optional for a compatible provider other than the default endpoint:
export WELLNOTE_AI_BASE_URL="https://your-provider.example/v1"
python app.py
```

`WELLNOTE_AI_BASE_URL` defaults to `https://api.openai.com/v1`. The model's
knowledge and reliability depend on the configured provider and model; answers
can be incomplete or incorrect. Wellnote does not guarantee comprehensive
world knowledge. Provider errors are shown in the study buddy instead of being
silently replaced with a canned answer.

## What's included

- Searchable disease guides with descriptions, common symptoms, prevention,
  treatment context, and a link to a health authority.
- Searches outside the curated guides use the U.S. National Library of
  Medicine's MedlinePlus health-topics API and show linked, source-attributed
  summaries. If the reference service is unavailable or has no result, the app
  says so and offers MedlinePlus directly instead of inventing details.
- A saved-topics list stored in a browser cookie.
- A study room with rotating greetings, a configurable AI study companion (or
  curated local replies when no AI provider is configured),
  introductory original practice questions, and answer explanations.
- A study-buddy overview of all 13 essential vitamins, common deficiency
  findings, dietary sources, a link to NIH fact sheets, and clinical safety context.
- NEET, MCAT, and AAMC study prompts that point learners toward official
  information; the app does not reproduce official exam questions.
- Responsive styling, accessible form labels, and medical-learning disclaimers.

## Scope and safety

The built-in disease library and local tutor provide curated educational
examples—not an exhaustive database, a diagnostic system, or a full exam
preparation course. Generative answers require the optional configured provider
and are not guaranteed complete or correct.
Unknown disease searches use the external
MedlinePlus service and require an internet connection; it may not have an
article for every topic. Medical information is for general education and is
not personal medical advice. For
symptoms, diagnosis, or treatment, consult a qualified health professional; for
a possible emergency, contact local emergency services. Confirm exam syllabi and
rules with the relevant official exam provider.

To extend the app, add reviewed disease entries and their references to
`diseases.py`, or original, checked practice questions to `study.py`.
