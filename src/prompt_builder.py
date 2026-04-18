"""
prompt_builder.py
-----------------
Build naive and structured prompts from product metadata.

This module is the core "Control Mechanism" of the pipeline:
  - Naive prompts  → simple product title only (baseline)
  - Structured prompts → rich template with brand, color, style cues
  - Negative prompts  → shared suppress-bad-output string
"""

from typing import Dict


# ── Negative prompt (shared across all generations) ──────────────────────────
NEGATIVE_PROMPT = (
    "blurry, low quality, low resolution, distorted, disfigured, "
    "text, watermark, logo, signature, duplicate, person, hands, body parts, "
    "cluttered background, busy background, cartoon, painting, drawing, "
    "anime, sketch, illustration, oversaturated, dark, grainy, noisy"
)

# ── Category-specific style cues ─────────────────────────────────────────────
CATEGORY_STYLE_MAP = {
    "electronics":    "professional product photography, studio lighting, minimal white background",
    "headphones":     "professional product photography, studio lighting, minimal white background, "
                      "floating product view",
    "earbuds":        "professional product photography, studio white background, macro detail shot",
    "televisions":    "professional product photography, front-facing, dark background with subtle glow",
    "e-readers":      "professional product photography, soft studio light, white background",
    "smartwatches":   "professional product photography, wrist display mockup, white background",
    "power banks":    "professional product photography, studio white background, clean shadows",
    "shoes":          "professional footwear photography, side profile, white studio background",
    "jeans":          "professional apparel photography, flat lay, white background",
    "jackets":        "professional apparel photography, ghost mannequin, white background",
    "sunglasses":     "professional eyewear photography, white background, soft shadow",
    "kitchen":        "professional kitchen product photography, marble surface, soft studio light",
    "coffee makers":  "professional kitchen product photography, marble countertop, warm studio light",
    "pressure cookers": "professional kitchen product photography, white background, soft shadow",
    "dutch ovens":    "professional kitchen product photography, white background, dramatic lighting",
    "blenders":       "professional kitchen product photography, white background, clean shot",
    "stand mixers":   "professional kitchen product photography, white marble surface",
    "tumblers":       "professional product photography, white background, condensation detail",
    "vacuum cleaners": "professional product photography, white background, sleek angle shot",
    "building blocks": "professional toy photography, white background, colorful arrangement",
    "default":        "professional product photography, studio lighting, white background",
}


def _get_style_cue(category: str) -> str:
    """Return the best-matching style cue for a product category."""
    category_lower = category.lower()
    for key, style in CATEGORY_STYLE_MAP.items():
        if key in category_lower:
            return style
    return CATEGORY_STYLE_MAP["default"]


# ── Prompt builders ───────────────────────────────────────────────────────────

def build_naive_prompt(product: Dict) -> str:
    """
    Baseline prompt: product title only.
    Example: "Sony WH-1000XM4 Wireless Noise Cancelling Headphones"
    """
    return product["title"]


def build_structured_prompt(product: Dict) -> str:
    """
    Structured prompt: rich template combining metadata fields and style cues.

    Template structure:
      {style cue}, {brand} {title}, {color}, {material hint},
      sharp details, 8K resolution, product advertisement style,
      isolated product, no background clutter
    """
    title    = product.get("title", "product")
    brand    = product.get("brand", "")
    color    = product.get("color", "")
    material = product.get("material", "")
    category = product.get("category", "")
    attrs    = product.get("attributes", "")

    style_cue = _get_style_cue(category)

    # Build attribute hint (first 2 attributes only to keep prompt concise)
    attr_hint = ""
    if attrs:
        attr_list = [a.strip() for a in attrs.split(",")][:2]
        attr_hint = ", ".join(attr_list)

    # Compose the structured prompt
    parts = [
        style_cue,
        f"{brand} {title}",
        f"{color} color" if color else "",
        f"{material}" if material else "",
        attr_hint,
        "sharp focus, 8K resolution, product advertisement quality",
        "isolated product on clean background, commercial photography",
    ]

    # Filter empty parts and join
    prompt = ", ".join(p for p in parts if p.strip())
    return prompt


def build_negative_prompt() -> str:
    """Return the shared negative prompt string."""
    return NEGATIVE_PROMPT


def describe_prompt_strategy() -> str:
    """
    Return a human-readable description of the prompt strategy for the report.
    """
    return """
Prompt Strategy Overview
========================
1. NAIVE (Baseline):
   - Input: product title only
   - Example: "Sony WH-1000XM4 Wireless Noise Cancelling Headphones"
   - Problem: Vague, no style guidance → inconsistent, often noisy backgrounds

2. STRUCTURED (Improved):
   - Input: brand + title + color + material + category-specific style cue
   - Example: "professional product photography, studio lighting, minimal white
     background, Sony WH-1000XM4 Wireless Noise Cancelling Headphones, Black
     color, Plastic Foam, over-ear foldable, sharp focus, 8K resolution,
     product advertisement quality, isolated product on clean background"
   - Result: Consistent studio-style shots, correct color, clean background

3. NEGATIVE PROMPT (always applied):
   - Suppresses: blurriness, text/watermarks, cluttered backgrounds, people,
     cartoon/illustration artifacts, low quality
"""


# ── Quick sanity check ───────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = {
        "asin": "B08N5WRWNW",
        "title": "Sony WH-1000XM4 Wireless Noise Cancelling Headphones",
        "category": "Electronics > Headphones",
        "brand": "Sony",
        "color": "Black",
        "material": "Plastic, Foam",
        "attributes": "over-ear, foldable, 30hr battery, USB-C charging",
    }

    print("=== NAIVE PROMPT ===")
    print(build_naive_prompt(sample))
    print()
    print("=== STRUCTURED PROMPT ===")
    print(build_structured_prompt(sample))
    print()
    print("=== NEGATIVE PROMPT ===")
    print(build_negative_prompt())
    print()
    print(describe_prompt_strategy())
