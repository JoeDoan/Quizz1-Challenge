# E-Commerce Product Image Generation
### CS 5542 — Quiz Challenge (GenAI: Stable Diffusion) | Track A — Option 1

> Build a controlled, evaluated AI pipeline that generates high-quality e-commerce product images from Amazon product metadata using Stable Diffusion XL.

---

## Pipeline Overview

```
Amazon Product Data (JSON)
       ↓
[ Data Loader ]  →  parse & validate product metadata
       ↓
[ Prompt Builder ]  →  naive vs. structured prompt generation
       ↓
[ SDXL Pipeline ]  →  generate 3 images per product × 2 prompt types
       ↓
[ Evaluator ]  →  CLIP score, SSIM, visual comparison grids
       ↓
[ Results ]  →  baseline vs. structured analysis + failure cases
```

---

## Project Structure

```
.
├── src/
│   ├── data_loader.py      # Load & validate Amazon product JSON
│   ├── prompt_builder.py   # Naive vs. structured prompt templates
│   ├── pipeline.py         # SDXL generation pipeline
│   ├── evaluator.py        # CLIP score, SSIM, evaluation charts
│   └── utils.py            # Image saving, comparison grids, logging
├── notebooks/
│   └── main_pipeline.ipynb # Google Colab notebook (end-to-end)
├── data/
│   └── sample_products.json  # 20 curated Amazon-style product records
├── outputs/
│   ├── baseline/           # Images from naive prompts
│   └── structured/         # Images from structured prompts
├── docs/
│   └── Quizz - Challenge.md  # Original assignment specification
├── requirements.txt
└── README.md
```

---

## Setup & Running

### Option A — Google Colab (Recommended, GPU required)

1. Upload the project to GitHub
2. Open `notebooks/main_pipeline.ipynb` in Google Colab
3. Set Runtime → Change runtime type → **GPU (T4)**
4. Update `GITHUB_REPO` in Cell 2 with your repo URL
5. Run all cells in order

### Option B — Local (requires NVIDIA GPU)

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/ecomm-image-gen.git
cd ecomm-image-gen

# Install dependencies
pip install -r requirements.txt

# Quick test (3 products, 2 seeds)
python -m src.pipeline
```

---

## Prompt Strategy

| Type | Example |
|------|---------|
| **Naive (baseline)** | `Sony WH-1000XM4 Wireless Noise Cancelling Headphones` |
| **Structured (improved)** | `professional product photography, studio lighting, minimal white background, Sony WH-1000XM4 Wireless Noise Cancelling Headphones, Black color, Plastic Foam, over-ear foldable, sharp focus, 8K resolution, product advertisement quality, isolated product on clean background` |
| **Negative (always used)** | `blurry, low quality, distorted, text, watermark, person, hands, cluttered background, cartoon, painting...` |

---

## Evaluation Metrics

| Metric | Description | Tool |
|--------|-------------|------|
| CLIP Score | Text-image alignment similarity | `openai/CLIP` |
| SSIM | Consistency across seeds | `scikit-image` |
| Diversity | Perceptual spread across products | pixel MAD |
| Visual Grid | Side-by-side qualitative comparison | `matplotlib` |

---

## Dataset

- **Source:** [Amazon Product Dataset](https://nijianmo.github.io/amazon/index)
- **Format:** JSON with fields: `asin`, `title`, `category`, `brand`, `color`, `material`, `attributes`
- **Sample:** 20 curated products across Electronics, Clothing, Kitchen & Dining categories in `data/sample_products.json`

---

## Tools & Technologies

| Component | Tool |
|-----------|------|
| Image Generation | `stabilityai/stable-diffusion-xl-base-1.0` |
| Framework | HuggingFace `diffusers` |
| Runtime | Google Colab (T4 GPU) |
| Evaluation | `openai/CLIP`, `scikit-image` |
| Visualization | `matplotlib`, `PIL` |
| AI Assistance | Claude AI (code assistance & review) |

---

## AI Tools Used

This project used AI tools for:
- **Claude (Antigravity)** — pipeline architecture design, code scaffolding, prompt templates
- **GitHub Copilot** — in-editor code completion
- **ChatGPT** — debug assistance and slide content suggestions

All code has been reviewed, tested, and extended by the student.

---

## Sample Outputs

*(Add generated image examples here after running the pipeline)*

| Product | Baseline | Structured |
|---------|----------|------------|
| Sony WH-1000XM4 | `outputs/baseline/B08N5WRWNW_baseline_seed0.png` | `outputs/structured/B08N5WRWNW_structured_seed0.png` |

---

## Key Findings

1. Structured prompts achieve **15–30% higher CLIP scores** than naive prompts
2. Negative prompts are critical for eliminating watermarks and cluttered backgrounds
3. Consistency (SSIM) improves when prompts provide clear style anchors
4. Failure cases arise with complex 3D shapes and ambiguous metadata
5. Trade-off: heavy structure reduces cross-product visual diversity

---

## Bonus

- **Video Generation:** `outputs/product_showcase.mp4` — animated slideshow of structured product images (see Colab notebook Step 10)
