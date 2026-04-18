"""
evaluator.py
------------
Evaluation metrics for generated product images.

Metrics:
  1. CLIP Score      – prompt-image alignment (text ↔ image similarity)
  2. SSIM            – consistency across seeds (structural similarity)
  3. Diversity Score – perceptual distance across different products
  4. Visual Grid     – qualitative side-by-side comparison
"""

import os
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path

from PIL import Image
from src.utils import get_logger, ensure_dir, save_results_json

logger = get_logger("evaluator")


# ── 1. CLIP Score (Prompt Alignment) ─────────────────────────────────────────

def compute_clip_score(
    image_paths: List[str],
    prompt: str,
    clip_model=None,
    clip_preprocess=None,
    device: str = "cuda",
) -> float:
    """
    Compute average CLIP cosine similarity between a prompt and a list of images.

    Args:
        image_paths:     Paths to generated images.
        prompt:          The text prompt used for generation.
        clip_model:      Pre-loaded CLIP model (loaded once externally).
        clip_preprocess: CLIP image preprocessor.
        device:          'cuda' or 'cpu'

    Returns:
        Average CLIP score (0–1, higher is better).
    """
    import torch
    import clip

    if clip_model is None:
        logger.info("Loading CLIP model (ViT-B/32)...")
        clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)

    text_tokens = clip.tokenize([prompt]).to(device)
    scores = []

    for path in image_paths:
        if not os.path.exists(path):
            continue
        image = clip_preprocess(Image.open(path)).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = clip_model.encode_image(image)
            text_features  = clip_model.encode_text(text_tokens)
            # Normalize
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features  = text_features  / text_features.norm(dim=-1, keepdim=True)
            score = (image_features @ text_features.T).item()
        scores.append(score)

    return float(np.mean(scores)) if scores else 0.0


# ── 2. SSIM (Consistency across seeds) ───────────────────────────────────────

def compute_ssim_consistency(image_paths: List[str]) -> float:
    """
    Compute average SSIM between all pairs of images.
    High SSIM = high consistency across seeds for the same product.

    Args:
        image_paths: List of image file paths (one per seed).

    Returns:
        Average pairwise SSIM score (0–1).
    """
    from skimage.metrics import structural_similarity as ssim
    import skimage.color

    images = []
    for path in image_paths:
        if os.path.exists(path):
            img = np.array(Image.open(path).convert("RGB").resize((256, 256)))
            images.append(img)

    if len(images) < 2:
        return 1.0  # Only 1 image, trivially consistent

    pair_scores = []
    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            score = ssim(images[i], images[j], channel_axis=2, data_range=255)
            pair_scores.append(score)

    return float(np.mean(pair_scores))


# ── 3. Diversity Score (across products) ─────────────────────────────────────

def compute_diversity_score(all_image_paths: List[str]) -> float:
    """
    Measure average perceptual distance across images from different products.
    High diversity = the model can generate visually distinct products.

    Uses pixel-level mean absolute difference as a lightweight proxy.
    (Replace with LPIPS for more accurate results if GPU available.)

    Args:
        all_image_paths: Sample of image paths across different products.

    Returns:
        Average pairwise pixel distance (normalized 0–1).
    """
    images = []
    for path in all_image_paths[:10]:  # Cap at 10 for speed
        if os.path.exists(path):
            img = np.array(Image.open(path).convert("RGB").resize((128, 128))) / 255.0
            images.append(img)

    if len(images) < 2:
        return 0.0

    pair_dists = []
    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            dist = np.mean(np.abs(images[i] - images[j]))
            pair_dists.append(dist)

    return float(np.mean(pair_dists))


# ── 4. Full evaluation run ────────────────────────────────────────────────────

def evaluate_results(
    baseline_results:   List[Dict],
    structured_results: List[Dict],
    output_dir: str,
    device: str = "cuda",
) -> List[Dict]:
    """
    Run all metrics on baseline and structured results, return a comparison table.

    Args:
        baseline_results:   List of {asin, title, prompt, image_paths} from pipeline.
        structured_results: Same structure for structured prompts.
        output_dir:         Where to save the evaluation report.
        device:             'cuda' or 'cpu'

    Returns:
        List of per-product evaluation dicts.
    """
    try:
        import clip
        import torch
        logger.info("Loading CLIP model...")
        clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
        clip_available = True
    except ImportError:
        logger.warning("CLIP not installed. Skipping CLIP scores.")
        clip_model = clip_preprocess = None
        clip_available = False

    # Build asin → result lookup
    structured_lookup = {r["asin"]: r for r in structured_results}

    evaluation = []
    for base_rec in baseline_results:
        asin  = base_rec["asin"]
        title = base_rec["title"]
        struct_rec = structured_lookup.get(asin, {})

        base_paths   = base_rec.get("image_paths", [])
        struct_paths = struct_rec.get("image_paths", [])

        # CLIP scores
        base_clip   = 0.0
        struct_clip = 0.0
        if clip_available:
            base_clip   = compute_clip_score(
                base_paths, base_rec.get("prompt", ""), clip_model, clip_preprocess, device)
            struct_clip = compute_clip_score(
                struct_paths, struct_rec.get("prompt", ""), clip_model, clip_preprocess, device)

        # SSIM consistency
        base_ssim   = compute_ssim_consistency(base_paths)
        struct_ssim = compute_ssim_consistency(struct_paths)

        record = {
            "asin":                    asin,
            "title":                   title,
            "baseline_clip_score":     round(base_clip,   4),
            "structured_clip_score":   round(struct_clip, 4),
            "clip_improvement":        round(struct_clip - base_clip, 4),
            "baseline_ssim":           round(base_ssim,   4),
            "structured_ssim":         round(struct_ssim, 4),
            "ssim_improvement":        round(struct_ssim - base_ssim, 4),
            "baseline_images":         base_paths,
            "structured_images":       struct_paths,
            "has_error":               bool(base_rec.get("error") or struct_rec.get("error")),
        }
        evaluation.append(record)
        logger.info(
            f"  {title[:40]:<40} | "
            f"CLIP: {base_clip:.3f} → {struct_clip:.3f} "
            f"(+{struct_clip - base_clip:.3f}) | "
            f"SSIM: {base_ssim:.3f} → {struct_ssim:.3f}"
        )

    # Save results
    results_path = os.path.join(output_dir, "evaluation_results.json")
    save_results_json(evaluation, results_path)

    return evaluation


# ── 5. Summary report ─────────────────────────────────────────────────────────

def print_summary_table(evaluation: List[Dict]) -> None:
    """Print a formatted summary table to stdout."""
    print("\n" + "=" * 90)
    print(f"{'Product':<42} | {'CLIP Base':>9} | {'CLIP Strct':>10} | {'SSIM Base':>9} | {'SSIM Strct':>10}")
    print("=" * 90)
    for rec in evaluation:
        print(
            f"{rec['title'][:40]:<42} | "
            f"{rec['baseline_clip_score']:>9.4f} | "
            f"{rec['structured_clip_score']:>10.4f} | "
            f"{rec['baseline_ssim']:>9.4f} | "
            f"{rec['structured_ssim']:>10.4f}"
        )
    print("=" * 90)

    # Averages
    avg_base_clip   = np.mean([r["baseline_clip_score"]   for r in evaluation])
    avg_struct_clip = np.mean([r["structured_clip_score"] for r in evaluation])
    avg_base_ssim   = np.mean([r["baseline_ssim"]         for r in evaluation])
    avg_struct_ssim = np.mean([r["structured_ssim"]       for r in evaluation])

    print(f"\nAVERAGES:")
    print(f"  CLIP Score  — Baseline: {avg_base_clip:.4f}  |  Structured: {avg_struct_clip:.4f}  "
          f"| Δ = {avg_struct_clip - avg_base_clip:+.4f}")
    print(f"  SSIM        — Baseline: {avg_base_ssim:.4f}  |  Structured: {avg_struct_ssim:.4f}  "
          f"| Δ = {avg_struct_ssim - avg_base_ssim:+.4f}")


def generate_evaluation_grid(evaluation: List[Dict], output_dir: str) -> None:
    """
    Create a matplotlib figure showing CLIP score comparison bar chart.
    """
    import matplotlib.pyplot as plt

    titles   = [r["title"][:25] + "..." for r in evaluation]
    base_scores   = [r["baseline_clip_score"]   for r in evaluation]
    struct_scores = [r["structured_clip_score"] for r in evaluation]

    x     = np.arange(len(titles))
    width = 0.35

    fig, ax = plt.subplots(figsize=(max(12, len(titles) * 1.2), 6))
    bars1 = ax.bar(x - width/2, base_scores,   width, label="Baseline (naive)",    color="#e74c3c", alpha=0.85)
    bars2 = ax.bar(x + width/2, struct_scores, width, label="Structured prompt",   color="#2ecc71", alpha=0.85)

    ax.set_xlabel("Product", fontsize=12)
    ax.set_ylabel("CLIP Score (prompt alignment)", fontsize=12)
    ax.set_title("Baseline vs. Structured Prompt — CLIP Score Comparison", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(titles, rotation=45, ha="right", fontsize=8)
    ax.legend(fontsize=11)
    ax.set_ylim(0, 1.0)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    chart_path = os.path.join(output_dir, "clip_score_comparison.png")
    ensure_dir(output_dir)
    plt.savefig(chart_path, dpi=120, bbox_inches="tight")
    plt.close()
    logger.info(f"Evaluation chart saved → {chart_path}")
