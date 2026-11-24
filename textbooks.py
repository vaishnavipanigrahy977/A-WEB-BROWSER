"""Curated open textbook metadata and original WellNote learning aids."""


BOOKS = [
    {
        "id": "anatomy-and-physiology-2e",
        "title": "Anatomy and Physiology 2e",
        "subject": "Anatomy & physiology",
        "level": "Introductory college",
        "audience": "Foundations for health-science and allied-health learners",
        "authors": (
            "J. Gordon Betts, Peter Desaix, Eddie Johnson, Jody E. Johnson, "
            "Oksana Korol, Dean Kruse, Brandon Poe, James A. Wise, Mark Womble, "
            "and Kelly A. Young"
        ),
        "publisher": "OpenStax, Rice University",
        "source": "https://openstax.org/books/anatomy-and-physiology-2e",
        "license": "CC BY-NC-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "attribution": (
            "J. Gordon Betts et al., Anatomy and Physiology 2e, OpenStax, Rice "
            "University. Licensed under CC BY-NC-SA 4.0."
        ),
        "source_note": (
            "Metadata and chapter names are attributed to the official OpenStax "
            "book. Read the complete textbook at OpenStax."
        ),
        "chapters": [
            {
                "id": "introduction",
                "number": 1,
                "title": "An Introduction to the Human Body",
                "source_slug": "1-introduction",
                "summary": (
                    "Anatomy describes body structures, while physiology explains "
                    "how those structures function; both are organized across "
                    "levels from cells to organ systems."
                ),
                "glossary": [
                    ("Anatomy", "The study of the structure of the body and its parts."),
                    ("Physiology", "The study of how body structures function."),
                    ("Homeostasis", "Regulation that helps maintain a relatively stable internal environment."),
                ],
                "review": [
                    {
                        "question": "How do anatomy and physiology complement each other?",
                        "answer": (
                            "Anatomy describes what structures are present; physiology "
                            "explains how those structures work."
                        ),
                    },
                    {
                        "question": "Put these levels in order from smaller to larger: organ, cell, tissue.",
                        "answer": "Cell, tissue, organ.",
                    },
                ],
                "keywords": "structure function organization homeostasis cell tissue organ",
            },
            {
                "id": "cellular-level",
                "number": 3,
                "title": "The Cellular Level of Organization",
                "source_slug": "3-the-cellular-level-of-organization",
                "summary": (
                    "Cells are the smallest living units of the body, and their "
                    "membranes, organelles, and specialized activities support "
                    "tissues and organ systems."
                ),
                "glossary": [
                    ("Cell membrane", "A selective boundary between a cell and its surroundings."),
                    ("Organelle", "A specialized structure inside a cell that performs particular functions."),
                    ("Tissue", "A group of cells and their surrounding materials working together."),
                ],
                "review": [
                    {
                        "question": "What is one important role of a cell membrane?",
                        "answer": "It forms a selective boundary that helps regulate exchange with the surroundings.",
                    },
                    {
                        "question": "How are cells related to tissues?",
                        "answer": "Cells with coordinated roles combine with surrounding material to form tissues.",
                    },
                ],
                "keywords": "cell membrane organelle tissue nucleus transport",
            },
            {
                "id": "endocrine-system",
                "number": 17,
                "title": "The Endocrine System",
                "source_slug": "17-the-endocrine-system",
                "summary": (
                    "Endocrine glands release hormones into circulation; target "
                    "cells respond when they have receptors that recognize those "
                    "chemical signals."
                ),
                "glossary": [
                    ("Hormone", "A chemical messenger released by cells that can affect target cells."),
                    ("Target cell", "A cell with receptors that can respond to a particular signal."),
                    ("Endocrine gland", "A gland that releases its products into the body's internal environment."),
                ],
                "review": [
                    {
                        "question": "Why do hormones affect some cells but not others?",
                        "answer": "A cell generally responds only when it has receptors for the hormone.",
                    },
                    {
                        "question": "How do endocrine signals commonly reach distant target cells?",
                        "answer": "They travel through the circulation.",
                    },
                ],
                "keywords": "hormone gland target cell signal blood regulation",
            },
            {
                "id": "lymphatic-immunity",
                "number": 21,
                "title": "The Lymphatic System and Immunity",
                "source_slug": "21-the-lymphatic-system-and-immunity",
                "summary": (
                    "Lymphatic vessels return fluid to the circulation, while "
                    "lymphoid structures support immune-cell activity and the "
                    "body's defenses."
                ),
                "glossary": [
                    ("Lymph", "Fluid carried through lymphatic vessels."),
                    ("Lymph node", "A small lymphoid structure that filters lymph and supports immune activity."),
                    ("Lymphocyte", "A white blood cell involved in immune responses."),
                ],
                "review": [
                    {
                        "question": "Name one role of the lymphatic system.",
                        "answer": "It returns excess tissue fluid to the circulation and supports immune functions.",
                    },
                    {
                        "question": "What fluid moves through lymphatic vessels?",
                        "answer": "Lymph.",
                    },
                ],
                "keywords": "lymph lymphatic vessel node lymphocyte immunity fluid",
            },
        ],
    },
    {
        "id": "microbiology",
        "title": "Microbiology",
        "subject": "Microbiology & infection",
        "level": "Introductory college / allied health",
        "audience": "Single-semester microbiology, including allied-health foundations",
        "authors": (
            "Nina Parker, Mark Schneegurt, Anh-Hue Thi Tu, Brian M. Forster, "
            "and Philip Lister"
        ),
        "publisher": (
            "OpenStax, Rice University, in collaboration with the American "
            "Society for Microbiology Press"
        ),
        "source": "https://openstax.org/books/microbiology",
        "license": "CC BY-NC-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "attribution": (
            "Nina Parker et al., Microbiology, OpenStax, Rice University, in "
            "collaboration with the American Society for Microbiology Press. "
            "Licensed under CC BY-NC-SA 4.0."
        ),
        "source_note": (
            "Metadata and chapter names are attributed to the official OpenStax "
            "book. Read the complete textbook at OpenStax."
        ),
        "chapters": [
            {
                "id": "invisible-world",
                "number": 1,
                "title": "An Invisible World",
                "source_slug": "1-an-invisible-world",
                "summary": (
                    "Microorganisms are diverse and widespread; microbiology "
                    "studies them using evidence gathered through observation, "
                    "experimentation, and specialized tools."
                ),
                "glossary": [
                    ("Microorganism", "An organism too small to be seen clearly without magnification."),
                    ("Microbiology", "The study of microorganisms and related microscopic agents."),
                    ("Microscopy", "Methods that use instruments to observe small objects."),
                ],
                "review": [
                    {
                        "question": "Why are microscopes useful in microbiology?",
                        "answer": "They make many cells and structures visible for observation and study.",
                    },
                    {
                        "question": "Give one way microbiologists can investigate a claim.",
                        "answer": "They can design an observation or experiment and evaluate the evidence it produces.",
                    },
                ],
                "keywords": "microorganism microbiology microscope evidence observation",
            },
            {
                "id": "the-cell",
                "number": 3,
                "title": "The Cell",
                "source_slug": "3-the-cell",
                "summary": (
                    "Cell structure helps distinguish major groups of microbes; "
                    "comparing cellular features can explain differences in how "
                    "organisms grow and interact."
                ),
                "glossary": [
                    ("Prokaryote", "An organism whose cells do not enclose DNA in a nucleus."),
                    ("Eukaryote", "An organism whose cells contain a nucleus."),
                    ("Cell wall", "A structure outside some cell membranes that helps support and protect a cell."),
                ],
                "review": [
                    {
                        "question": "What is one structural distinction between prokaryotic and eukaryotic cells?",
                        "answer": "Eukaryotic cells have a nucleus; prokaryotic cells do not.",
                    },
                    {
                        "question": "Why compare cell structures across microorganisms?",
                        "answer": "Structural differences help classify organisms and understand how they function.",
                    },
                ],
                "keywords": "cell prokaryote eukaryote membrane cell wall nucleus",
            },
            {
                "id": "antimicrobial-drugs",
                "number": 14,
                "title": "Antimicrobial Drugs",
                "source_slug": "14-antimicrobial-drugs",
                "summary": (
                    "Antimicrobial agents act on microbial targets; selectivity "
                    "and resistance are important concepts when studying how "
                    "these medicines work."
                ),
                "glossary": [
                    ("Antimicrobial", "An agent that acts against microorganisms."),
                    ("Selective toxicity", "The principle of affecting a target organism more than its host."),
                    ("Antimicrobial resistance", "A microorganism's ability to survive exposure to an agent that previously inhibited it."),
                ],
                "review": [
                    {
                        "question": "What does selective toxicity aim to achieve?",
                        "answer": "It aims to inhibit or damage a microorganism while limiting harm to its host.",
                    },
                    {
                        "question": "Why is antimicrobial resistance important to study?",
                        "answer": "It can reduce how well an antimicrobial agent works against a microorganism.",
                    },
                ],
                "keywords": "antimicrobial drug selective toxicity resistance medicine",
            },
            {
                "id": "disease-epidemiology",
                "number": 16,
                "title": "Disease and Epidemiology",
                "source_slug": "16-disease-and-epidemiology",
                "summary": (
                    "Epidemiology examines patterns of health and disease in "
                    "populations, helping researchers describe trends and test "
                    "possible explanations."
                ),
                "glossary": [
                    ("Epidemiology", "The study of patterns and causes of health-related events in populations."),
                    ("Incidence", "The occurrence of new cases in a population over a defined period."),
                    ("Prevalence", "The number or proportion of existing cases in a population at a point or period in time."),
                ],
                "review": [
                    {
                        "question": "How does incidence differ from prevalence?",
                        "answer": "Incidence concerns new cases over time; prevalence describes existing cases in a population.",
                    },
                    {
                        "question": "Why study disease patterns across populations?",
                        "answer": "Patterns can help researchers describe distribution and investigate possible contributing factors.",
                    },
                ],
                "keywords": "epidemiology disease population incidence prevalence transmission",
            },
            {
                "id": "innate-defenses",
                "number": 17,
                "title": "Innate Nonspecific Host Defenses",
                "source_slug": "17-innate-nonspecific-host-defenses",
                "summary": (
                    "Innate defenses provide broad protective responses that can "
                    "act early, including physical barriers, cells, and soluble "
                    "immune factors."
                ),
                "glossary": [
                    ("Innate immunity", "Defenses present without requiring prior exposure to a particular pathogen."),
                    ("Barrier", "A physical or chemical feature that helps limit entry or spread of microbes."),
                    ("Inflammation", "A coordinated local response to injury or infection."),
                ],
                "review": [
                    {
                        "question": "What is one feature of innate defenses?",
                        "answer": "They provide broad protection and do not require prior exposure to a specific pathogen.",
                    },
                    {
                        "question": "What is one role of a physical barrier?",
                        "answer": "It can help prevent microbes from entering body tissues.",
                    },
                ],
                "keywords": "innate immunity host defense barrier inflammation pathogen",
            },
        ],
    },
]


BOOKS_BY_ID = {book["id"]: book for book in BOOKS}
CHAPTERS_BY_ID = {
    (book["id"], chapter["id"]): chapter
    for book in BOOKS
    for chapter in book["chapters"]
}
VALID_CHAPTER_KEYS = set(CHAPTERS_BY_ID)
