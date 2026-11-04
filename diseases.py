"""Small curated set of educational disease guides with trusted sources."""

DISEASES = [
    {
        "slug": "asthma",
        "name": "Asthma",
        "category": "Respiratory health",
        "summary": "A long-term condition that can make the airways inflamed and narrow.",
        "description": (
            "Asthma affects the airways that carry air into and out of the lungs. "
            "Airway inflammation and tightening can cause symptoms that vary over "
            "time. Triggers differ from person to person, and an individual care plan "
            "can help people recognize and manage worsening symptoms."
        ),
        "symptoms": ["Wheezing", "Cough, often at night or early morning", "Shortness of breath", "Chest tightness"],
        "prevention": [
            "Work with a clinician to identify personal triggers.",
            "Follow the written asthma action plan and prescribed treatment.",
            "Avoid tobacco smoke and reduce exposure to known irritants.",
            "Keep recommended vaccinations up to date.",
        ],
        "treatment": (
            "Asthma is a chronic condition and does not currently have a cure, "
            "but prescribed medicines and an action plan can help control symptoms. "
            "Treatment may include inhaled medicines; the right plan is individual."
        ),
        "study_points": [
            "Asthma affects the airways and symptoms can come and go.",
            "Common symptoms include wheezing, cough, breathlessness, and chest tightness.",
            "A clinician-supported action plan can help manage flare-ups.",
        ],
        "source_name": "National Heart, Lung, and Blood Institute",
        "source_url": "https://www.nhlbi.nih.gov/health/asthma",
    },
    {
        "slug": "type-2-diabetes",
        "name": "Type 2 diabetes",
        "category": "Metabolic health",
        "summary": "A condition in which blood glucose can become too high over time.",
        "description": (
            "Type 2 diabetes develops when the body does not use insulin effectively "
            "and, over time, may not make enough insulin to keep blood glucose in a "
            "healthy range. Risk and experience differ between people. A health "
            "professional can assess symptoms and testing and discuss a suitable plan."
        ),
        "symptoms": ["Increased thirst or urination", "Feeling more tired than usual", "Blurred vision", "Some people have no noticeable symptoms"],
        "prevention": [
            "Healthy habits may lower risk, but they cannot prevent every case.",
            "Discuss personal risk and screening with a health professional.",
            "Regular physical activity and balanced eating may support overall health.",
            "Risk is influenced by many factors; avoid blaming yourself.",
        ],
        "treatment": (
            "Type 2 diabetes is a long-term condition. A care plan may include "
            "nutrition and activity changes, monitoring, and medication. Some people "
            "can reach remission, but this is not guaranteed or the same as a cure; "
            "ongoing follow-up remains important."
        ),
        "study_points": [
            "The condition affects how the body uses insulin and manages blood glucose.",
            "Symptoms may include thirst, frequent urination, fatigue, or blurred vision.",
            "Testing and an individualized care plan should be discussed with a clinician.",
        ],
        "source_name": "Centers for Disease Control and Prevention",
        "source_url": "https://www.cdc.gov/diabetes/about/about-type-2-diabetes.html",
    },
    {
        "slug": "seasonal-influenza",
        "name": "Seasonal influenza (flu)",
        "category": "Infectious disease",
        "summary": "A contagious respiratory illness caused by influenza viruses.",
        "description": (
            "Seasonal influenza is an infection of the nose, throat, and sometimes "
            "lungs. It can range from mild to severe, and some people are at higher "
            "risk of complications. Symptoms can overlap with other illnesses, so "
            "this overview cannot identify the cause of an individual illness."
        ),
        "symptoms": ["Fever or feeling feverish and chills", "Cough and sore throat", "Muscle aches and headache", "Fatigue; some people also have a runny nose"],
        "prevention": [
            "Get the seasonal flu vaccine as recommended for you.",
            "Wash hands often and cover coughs and sneezes.",
            "Stay home when sick when possible and follow local health guidance.",
            "Ask a clinician promptly about care if you are at higher risk.",
        ],
        "treatment": (
            "Many people recover with rest and supportive care, but influenza can "
            "cause serious illness. Prescription antivirals may help some people, "
            "especially when started early. A clinician can advise on treatment; "
            "recovery is not guaranteed to follow the same course for everyone."
        ),
        "study_points": [
            "Influenza is a contagious respiratory illness caused by flu viruses.",
            "Fever, cough, sore throat, aches, and fatigue are common symptoms.",
            "Vaccination and everyday hygiene help lower risk; high-risk people should seek advice early.",
        ],
        "source_name": "Centers for Disease Control and Prevention",
        "source_url": "https://www.cdc.gov/flu/about/index.html",
    },
]

DISEASES_BY_SLUG = {item["slug"]: item for item in DISEASES}
