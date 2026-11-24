"""Recycling instructions for each waste category."""

# The six categories the app supports. Edit this list if the categories change.
CATEGORIES = ["Biodegradable", "Cardboard", "Glass", "Metal", "Paper", "Plastic"]

GUIDELINES = {
    "Biodegradable": [
        "Separate organic waste from recyclable materials.",
        "Compost suitable food scraps and organic materials.",
        "Avoid mixing compostable waste with plastic.",
    ],
    "Cardboard": [
        "Flatten cardboard boxes before recycling.",
        "Keep cardboard clean and dry.",
        "Remove excessive tape and packaging materials when possible.",
    ],
    "Glass": [
        "Empty and rinse glass containers.",
        "Separate glass from other recyclable materials.",
        "Handle broken glass carefully and follow local disposal guidelines.",
    ],
    "Metal": [
        "Empty and rinse metal cans and containers.",
        "Separate metal items from other waste.",
        "Check local recycling guidelines for accepted metal materials.",
    ],
    "Paper": [
        "Keep paper clean and dry.",
        "Separate paper from food-contaminated waste.",
        "Reuse paper when possible before recycling.",
    ],
    "Plastic": [
        "Empty and rinse plastic containers.",
        "Check local recycling guidelines for accepted plastic types.",
        "Separate plastic from other waste.",
    ],
}


def normalize_label(raw_name: str) -> str:
    """Turn a model class name like 'BIODEGRADABLE' or 'plastic_bottle' into 'Biodegradable'."""
    return raw_name.strip().replace("_", " ").replace("-", " ").title()


def get_guidelines(category: str):
    """Return the list of instructions for a category, or None if it is unknown."""
    return GUIDELINES.get(category)
