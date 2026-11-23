"""Curated anatomy learning content and licensed 3D model catalog."""

MODEL_REVISION = "6c7f9016bd5899ac8edafd31b9900c151df42ed6"
MODEL_BASE_URL = (
    "https://raw.githubusercontent.com/LluisV/Z-Anatomy/"
    f"{MODEL_REVISION}/Resources/Models/FBX/"
)

SYSTEMS = {
    "whole-body": {
        "label": "Whole body",
        "description": "A colourful interactive overview of the major organs and body systems.",
        "model": "",
        "size": "Instant",
    },
    "muscles": {
        "label": "Muscles",
        "description": "Explore the body's major muscles and supporting structures.",
        "model": "MuscularSystem100.fbx",
        "size": "37 MB",
    },
    "vessels": {
        "label": "Arteries & veins",
        "description": "Explore the cardiovascular system, including the heart and blood vessels.",
        "model": "CardioVascular41.fbx",
        "size": "65 MB",
    },
    "organs": {
        "label": "Organs",
        "description": "Explore the digestive, respiratory, urinary, and other visceral structures.",
        "model": "VisceralSystem100.fbx",
        "size": "18 MB",
    },
    "nervous": {
        "label": "Nervous system",
        "description": "Explore the brain, spinal cord, nerves, and sensory structures.",
        "model": "NervousSystem100.fbx",
        "size": "54 MB",
    },
    "lymphatic": {
        "label": "Lymphatic system",
        "description": "Explore lymphatic and immune structures throughout the body.",
        "model": "LymphoidOrgans100.fbx",
        "size": "2 MB",
    },
    "skeleton": {
        "label": "Skeleton",
        "description": "Explore the bones and joints that support and protect the body.",
        "model": "SkeletalSystem100.fbx",
        "size": "41 MB",
    },
}


LAYERS = {
    "organs": {
        "label": "Organs",
        "parts": [
            {
                "id": "brain",
                "name": "Brain",
                "system": "Nervous system",
                "summary": "The brain processes information and coordinates thought, senses, movement, and many automatic body functions.",
                "fact": "It communicates with the body through the spinal cord and nerves.",
            },
            {
                "id": "heart",
                "name": "Heart",
                "system": "Circulatory system",
                "summary": "The heart is a muscular pump that circulates blood through the lungs and the rest of the body.",
                "fact": "Its four chambers move blood through a one-way circuit.",
            },
            {
                "id": "lungs",
                "name": "Lungs",
                "system": "Respiratory system",
                "summary": "The lungs exchange oxygen and carbon dioxide between the air and the blood.",
                "fact": "The diaphragm helps draw air in and push it out.",
            },
            {
                "id": "liver",
                "name": "Liver",
                "system": "Digestive system",
                "summary": "The liver processes nutrients, makes bile, and helps break down substances carried in the blood.",
                "fact": "Blood from the digestive tract flows to the liver for processing.",
            },
            {
                "id": "stomach",
                "name": "Stomach",
                "system": "Digestive system",
                "summary": "The stomach stores and mixes swallowed food with acid and enzymes as part of digestion.",
                "fact": "Most nutrient absorption happens later in the small intestine.",
            },
            {
                "id": "kidneys",
                "name": "Kidneys",
                "system": "Urinary system",
                "summary": "The kidneys filter blood, help balance water and salts, and produce urine.",
                "fact": "Most people have two kidneys, one on each side of the spine.",
            },
        ],
    },
    "vessels": {
        "label": "Arteries & veins",
        "parts": [
            {
                "id": "aorta",
                "name": "Aorta",
                "system": "Artery",
                "summary": "The aorta carries oxygen-rich blood from the heart to the rest of the body.",
                "fact": "It is the body's largest artery.",
            },
            {
                "id": "vena-cava",
                "name": "Vena cava",
                "system": "Vein",
                "summary": "The vena cava returns oxygen-poor blood from the body to the heart.",
                "fact": "The superior and inferior vena cava enter the right atrium from above and below.",
            },
            {
                "id": "pulmonary-arteries",
                "name": "Pulmonary arteries",
                "system": "Arteries",
                "summary": "The pulmonary arteries carry oxygen-poor blood from the heart to the lungs.",
                "fact": "They are arteries even though they carry oxygen-poor blood.",
            },
            {
                "id": "pulmonary-veins",
                "name": "Pulmonary veins",
                "system": "Veins",
                "summary": "The pulmonary veins carry oxygen-rich blood from the lungs back to the heart.",
                "fact": "They are veins even though they carry oxygen-rich blood.",
            },
        ],
    },
    "muscles": {
        "label": "Muscles",
        "parts": [
            {
                "id": "deltoid",
                "name": "Deltoid",
                "system": "Shoulder muscle",
                "summary": "The deltoid covers the shoulder and helps lift and rotate the arm.",
                "fact": "It has front, middle, and rear portions that assist different arm movements.",
            },
            {
                "id": "biceps",
                "name": "Biceps",
                "system": "Upper-arm muscle",
                "summary": "The biceps helps bend the elbow and rotate the forearm.",
                "fact": "It works with other muscles to move the elbow and shoulder.",
            },
            {
                "id": "pectorals",
                "name": "Pectorals",
                "system": "Chest muscles",
                "summary": "The pectoral muscles help move the upper arm across the front of the chest.",
                "fact": "They attach the chest to the upper arm bone.",
            },
            {
                "id": "abdominals",
                "name": "Abdominals",
                "system": "Trunk muscles",
                "summary": "Abdominal muscles support the trunk and help with bending and turning.",
                "fact": "Together with back muscles, they help stabilize the torso.",
            },
            {
                "id": "quadriceps",
                "name": "Quadriceps",
                "system": "Thigh muscles",
                "summary": "The quadriceps group at the front of the thigh helps straighten the knee.",
                "fact": "These muscles are active during standing, walking, and climbing stairs.",
            },
            {
                "id": "calves",
                "name": "Calf muscles",
                "system": "Lower-leg muscles",
                "summary": "The calf muscles help point the foot and push the body forward while walking.",
                "fact": "The Achilles tendon connects major calf muscles to the heel.",
            },
        ],
    },
    "skeleton": {
        "label": "Skeleton",
        "parts": [
            {
                "id": "skull",
                "name": "Skull",
                "system": "Head bones",
                "summary": "The skull supports the face and protects the brain.",
                "fact": "The lower jaw is the skull's movable bone.",
            },
            {
                "id": "ribs",
                "name": "Rib cage",
                "system": "Chest bones",
                "summary": "The rib cage surrounds and helps protect the heart and lungs.",
                "fact": "Ribs connect to the spine; most also connect to the breastbone.",
            },
            {
                "id": "spine",
                "name": "Spine",
                "system": "Axial skeleton",
                "summary": "The spine supports the trunk and protects the spinal cord.",
                "fact": "It is made of stacked bones called vertebrae.",
            },
            {
                "id": "pelvis",
                "name": "Pelvis",
                "system": "Hip bones",
                "summary": "The pelvis supports the trunk and connects the spine with the legs.",
                "fact": "The hip joints connect the pelvis to the thigh bones.",
            },
            {
                "id": "humerus",
                "name": "Humerus",
                "system": "Upper-arm bone",
                "summary": "The humerus is the long bone in the upper arm.",
                "fact": "It connects the shoulder to the elbow.",
            },
            {
                "id": "femur",
                "name": "Femur",
                "system": "Thigh bone",
                "summary": "The femur is the long bone in the thigh and carries weight during movement.",
                "fact": "It is the longest bone in the human body.",
            },
        ],
    },
}


SHAPES = {
    "brain": '<path d="M176 63c-12-9-23 2-19 13-9 10 0 25 11 25 4 11 18 10 22 2V68c-4-7-9-8-14-5zm24 0c12-9 23 2 19 13 9 10 0 25-11 25-4 11-18 10-22 2V68c4-7 9-8 14-5z"/>',
    "heart": '<path d="M200 292c-7-10-25-20-25-35 0-17 22-21 25-5 4-16 25-12 25 5 0 15-18 25-25 35z"/>',
    "lungs": '<path d="M187 207c-13-23-31-13-39 9-9 24-11 53-4 68 7 12 21 9 38-1l18-15v-53c-4 1-9-2-13-8zm26 0c13-23 31-13 39 9 9 24 11 53 4 68-7 12-21 9-38-1l-18-15v-53c4 1 9-2 13-8z"/>',
    "liver": '<path d="M150 306c16-16 49-18 72-8 11 5 17 18 7 28-14 14-42 21-70 15-18-4-22-21-9-35z"/>',
    "stomach": '<path d="M224 315c12-12 20-7 18 6-2 12 11 15 13 28 3 19-17 34-37 27-16-6-20-22-11-34 7-9 10-17 8-27-1-5 3-8 9 0z"/>',
    "kidneys": '<path d="M158 364c-18-9-30 7-25 24 5 17 21 19 30 7 5-7 4-12 0-17 7-7 4-11-5-14zm84 0c18-9 30 7 25 24-5 17-21 19-30 7-5-7-4-12 0-17-7-7-4-11 5-14z"/>',
    "aorta": '<path d="M200 292V220c0-25 36-39 49-18 12 18-3 32-19 31m-30 18h-46l-31-39m31 39-35 47m81-47h45l31-39m-31 39 35 47m-49-91v145l-29 31m29-31 29 31v94m-58-94-29 31v94" fill="none" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>',
    "vena-cava": '<path d="M225 292V166m0 28h-44l-28-35m28 35-33 42m77-42h44l28-35m-28 35 33 42m-77-70v188l-26 35m26-35 26 35v111m-52-111-26 35v111" fill="none" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>',
    "pulmonary-arteries": '<path d="M200 292v-43m0 0-17-18m17 18 17-18m-17 18-28-8-19-24m19 24-6 28m51-20 19-32m-19 32 7 28" fill="none" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>',
    "pulmonary-veins": '<path d="M200 292v-43m0 0-17-18m17 18 17-18m-17 18h-38m0 0-20-19m20 19-18 22m73-22h38m0 0 20-19m-20 19 18 22" fill="none" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>',
    "deltoid": '<path d="M124 153c-18 4-30 17-31 34-1 14 9 20 24 13l18-24-11-23zm152 0c18 4 30 17 31 34 1 14-9 20-24 13l-18-24 11-23z"/>',
    "biceps": '<path d="M94 202c-8 22-15 47-18 71l18 13c14-25 23-53 26-75l-26-9zm212 0c8 22 15 47 18 71l-18 13c-14-25-23-53-26-75l26-9z"/>',
    "pectorals": '<path d="M145 190c18-13 37-13 52-5v50c-24 3-45-4-54-18-6-9-5-20 2-27zm110 0c-18-13-37-13-52-5v50c24 3 45-4 54-18 6-9 5-20-2-27z"/>',
    "abdominals": '<path d="M168 246h27v29h-27zm37 0h27v29h-27zm-37 37h27v29h-27zm37 0h27v29h-27z"/>',
    "quadriceps": '<path d="M145 382c-15 14-18 39-16 72l8 67c2 15 14 20 23 8 8-11 9-43 13-67l10-65-38-15zm110 0c15 14 18 39 16 72l-8 67c-2 15-14 20-23 8-8-11-9-43-13-67l-10-65 38-15z"/>',
    "calves": '<path d="M145 531c-11 18-13 45-12 74 1 19 13 22 22 6 8-15 11-44 12-67l-22-13zm110 0c11 18 13 45 12 74-1 19-13 22-22 6-8-15-11-44-12-67l22-13z"/>',
    "skull": '<path d="M169 57c0-23 13-37 31-37s31 14 31 37c0 17-8 25-16 31v15h-30V88c-8-6-16-14-16-31zm16 48h30v10h-30z"/>',
    "ribs": '<path fill="none" d="M200 152v119m-2-108c-16-13-43-8-46 6 14 14 29 18 46 15m4-21c16-13 43-8 46 6-14 14-29 18-46 15m-48-2c-11 7-13 16 0 23 14 7 29 7 44 2m4-25c11 7 13 16 0 23-14 7-29 7-44 2m44-2c15 5 30 5 44-2 13-7 11-16 0-23m-44 48c-15 5-30 5-44-2-13-7-11-16 0-23m44 25c15 5 30 5 44-2 13-7 11-16 0-23m-88 25c14-6 28-6 44-2m0 0c16-4 30-4 44 2"/>',
    "spine": '<path d="M200 120v261" fill="none" stroke-width="13" stroke-linecap="round"/><g class="bone-knuckles"><circle cx="200" cy="142" r="8"/><circle cx="200" cy="164" r="8"/><circle cx="200" cy="186" r="8"/><circle cx="200" cy="208" r="8"/><circle cx="200" cy="230" r="8"/><circle cx="200" cy="252" r="8"/><circle cx="200" cy="274" r="8"/><circle cx="200" cy="296" r="8"/><circle cx="200" cy="318" r="8"/><circle cx="200" cy="340" r="8"/><circle cx="200" cy="362" r="8"/></g>',
    "pelvis": '<path d="M163 350c-18 5-25 22-17 37l27 30 27-17 27 17 27-30c8-15 1-32-17-37l-37 15-37-15z"/>',
    "humerus": '<path d="M132 167l-31 112m137-112 31 112" fill="none" stroke-width="18" stroke-linecap="round"/>',
    "femur": '<path d="M177 392l-21 163m67-163 21 163" fill="none" stroke-width="23" stroke-linecap="round"/>',
}
