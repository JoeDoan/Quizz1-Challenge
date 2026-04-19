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

### Option B — Local (requires NVIDIA GPU or Apple Silicon MPS)

```bash
# Clone the repo
git clone https://github.com/JoeDoan/Quizz1-Challenge.git
cd Quizz1-Challenge

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
| Diversity | Perceptual spread across seeds | pixel MAD |
| Visual Grid | Side-by-side qualitative comparison | `matplotlib` |

---

## Dataset

- **Source:** [Amazon Product Dataset](https://nijianmo.github.io/amazon/index)
- **Format:** JSON with fields: `asin`, `title`, `category`, `brand`, `color`, `material`, `attributes`
- **Sample:** 20 curated products across Electronics, Clothing, Kitchen & Dining categories in `data/sample_products.json`
- **Evaluated:** 10 products were evaluated end-to-end (baseline + structured) due to Colab GPU quota. The full 20-product dataset can be reproduced by running all cells in the Colab notebook.

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

*Note: The individual 60 generated images (baseline and structured) are omitted from this repository to save space. You can reproduce them entirely by running the Colab notebook. Instead, we provide side-by-side comparison grids.*

| Product | Comparison Grid | Verdict |
|---------|-----------------|---------|
| **Nike Air Max 270** | [`outputs/grid_B09G9MX9QG.png`](outputs/grid_B09G9MX9QG.png) | ⭐ **Huge Improvement:** Baseline created a chaotic cartoon collage; structured created perfect isolated studio photography. |
| **Apple AirPods Pro** | [`outputs/grid_B07PXGQC1Q.png`](outputs/grid_B07PXGQC1Q.png) | ⭐ **Success:** High structural consistency and clean white background. |
| **Levi's 511 Jeans** | [`outputs/grid_B09B2K4H3R.png`](outputs/grid_B09B2K4H3R.png) | ⚠️ **Failure Case:** Baseline generated close-up pants/texture, structured generated an actual human model. |

### Evaluation Charts

| Chart | Description |
|-------|-------------|
| [`outputs/clip_score_comparison.png`](outputs/clip_score_comparison.png) | CLIP score (prompt alignment) — baseline vs. structured |
| [`outputs/ssim_consistency_comparison.png`](outputs/ssim_consistency_comparison.png) | SSIM consistency — structured prompts dramatically improve cross-seed reproducibility |

---

## Key Findings

1. **SSIM Consistency Improvement:** Structured prompts anchor the model's visual understanding much stronger. The average structural similarity across different seeds improved significantly (+0.13 average gain, from 0.34 to 0.47).
2. **CLIP Score Nuances:** While structured prompts give better subjective visuals, average CLIP scores occasionally regress slightly (0.307 down to 0.303). Complex prompts with many details sometimes dilute the primary subject token concentration for the CLIP text encoder.
3. **Negative Prompts are Essential:** They drastically reduced watermarks, messy background clutter, and illustration-style generations present in the baseline outputs.
4. **Apparel Limitation:** Diffusion models struggle to generate "ghost mannequin" or flat-laid clothing without defaulting to generating human models wearing them, as seen in the Levi's Jeans grid.
5. **Appliance "Knowledge" Bias:** For standard appliances (Instant Pot, Coffee Maker), the naive baseline and structured prompts yielded very similar results because the diffusion model already has a strong canonical representation of these items.

---

## Bonus

- **Video Generation:** `outputs/product_showcase.mp4` — animated slideshow of structured product images (see Colab notebook Step 10)
