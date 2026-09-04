"""
Smart Complaint & Service Management System
Priority Classifier (Phase 1 - standalone, no Django needed yet)

This module takes complaint text and returns:
    - category   (e.g. Electrical, Plumbing, Water, Furniture, General)
    - priority   (HIGH / MEDIUM / LOW)

It works on plain text, so it doesn't matter whether the text came from
a typed form OR from voice-to-text - both paths use this same function.

Run this file directly to test it with sample complaints before wiring
it into Django.
"""

# ---------------------------------------------------------------------
# STEP 1: Keyword banks
# Add/remove words here as you test more real complaint examples.
# Keep everything lowercase - we lowercase the input text before matching.
# ---------------------------------------------------------------------

HIGH_PRIORITY_KEYWORDS = [
    "fire", "spark", "sparking", "smoke", "gas leak", "gas smell",
    "flood", "flooding", "electrical panel", "short circuit",
    "exposed wire", "live wire", "water leaking near electrical",
    "collapse", "collapsed", "ceiling fall", "no water supply",
    "electric shock", "burning smell","electric shock",
"electrical fire",
"fire hazard",
"dangerous",
"emergency",
"urgent",
"burst pipe",
"water flooding",
"major leak",
"gas leakage",
"gas leaking",
]

MEDIUM_PRIORITY_KEYWORDS = [
    "not working", "noise", "leaking", "leak", "broken", "crack",
    "cracked", "flickering", "slow", "smell", "blocked", "clogged",
    "not cooling", "not heating", "loose", "damaged", "stuck","not functioning",
"malfunction",
"unstable",
"intermittent",
"poor connection",
"low pressure",
"water dripping",
]

LOW_PRIORITY_KEYWORDS = [
    "replace", "repaint", "paint", "cosmetic", "old", "faded",
    "request", "upgrade", "suggestion", "minor", "notice board",
    "cleaning", "dust", "dusty",
]

# ---------------------------------------------------------------------
# STEP 2: Category keyword banks
# Used to guess a category from the same text.
# ---------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "Electrical": [
        "electrical",
        "electric",
        "wire",
        "wiring",
        "switch",
        "switchboard",
        "socket",
        "plug",
        "fan",
        "light",
        "bulb",
        "panel",
        "short circuit",
        "spark",
        "sparking",
        "shock",
        "power",
        "current",
        "voltage",
    ],

    "Plumbing/Water": [
        "water",
        "leak",
        "leaking",
        "leakage",
        "pipe",
        "tap",
        "flood",
        "flooding",
        "drain",
        "clogged",
        "clog",
        "bathroom",
        "toilet",
        "washroom",
        "water supply",
    ],

    "Network/IT": [
        "wifi",
        "wi-fi",
        "internet",
        "network",
        "router",
        "connection",
        "connectivity",
        "computer",
        "projector",
        "laptop",
        "printer",
        "keyboard",
        "mouse",
        "software",
        "system",
        "server",
        "login",
        "website",
    ],

    "Furniture": [
        "chair",
        "table",
        "desk",
        "bench",
        "door",
        "window",
        "furniture",
        "bed",
        "cupboard",
        "wardrobe",
        "shelf",
        "drawer",
    ],

    "Cleanliness": [
        "dust",
        "dusty",
        "clean",
        "cleaning",
        "garbage",
        "trash",
        "waste",
        "dirty",
        "dirt",
        "hygiene",
        "litter",
    ],

    "General": [],
}


def detect_category(text: str) -> str:
    """
    Detect the complaint category based on keyword frequency.
    Returns General if no category matches.
    """

    text_lower = text.lower()

    category_scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0

        for keyword in keywords:
            if keyword in text_lower:
                score += 1

        if score > 0:
            category_scores[category] = score

    if not category_scores:
        return "General"

    return max(
        category_scores,
        key=category_scores.get
    )


def detect_priority(text: str) -> str:
    """Check HIGH keywords first, then MEDIUM, then LOW.
    Order matters: a sentence might contain both a MEDIUM word (e.g. 'leak')
    and a HIGH word (e.g. 'electrical panel') - HIGH should win."""
    text_lower = text.lower()

    for keyword in HIGH_PRIORITY_KEYWORDS:
        if keyword in text_lower:
            return "HIGH"

    for keyword in MEDIUM_PRIORITY_KEYWORDS:
        if keyword in text_lower:
            return "MEDIUM"

    for keyword in LOW_PRIORITY_KEYWORDS:
        if keyword in text_lower:
            return "LOW"

    # Default: if nothing matches, treat as MEDIUM so nothing is
    # accidentally ignored as LOW priority.
    return "MEDIUM"


def classify_complaint(text: str) -> dict:
    """Main function you'll call from Django later.
    Returns a dictionary with category and priority."""
    return {
        "text": text,
        "category": detect_category(text),
        "priority": detect_priority(text),
    }


# ---------------------------------------------------------------------
# STEP 3: Test cases - run this file directly to see it working
# ---------------------------------------------------------------------

if __name__ == "__main__":
    sample_complaints = [
        "Water is leaking near the electrical panel and the floor is getting flooded.",
        "The classroom fan is making a small noise.",
        "Please replace the old notice board.",
        "There is a burning smell coming from the switch board.",
        "Wifi is not working in the hostel block C.",
        "The chair in room 214 is broken.",
        "Can we get the walls repainted, they look old.",
    ]

    print("=" * 70)
    print("SMART COMPLAINT CLASSIFIER - TEST RUN")
    print("=" * 70)

    for complaint in sample_complaints:
        result = classify_complaint(complaint)
        print(f"\nComplaint : {result['text']}")
        print(f"Category  : {result['category']}")
        print(f"Priority  : {result['priority']}")

    print("\n" + "=" * 70)
    print("Test complete. Try changing the sentences above and re-run")
    print("this file to see how the classifier responds.")
    print("=" * 70)