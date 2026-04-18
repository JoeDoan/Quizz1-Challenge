"""
utils.py
--------
Utility helpers: image saving, directory management, logging, grids.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from PIL import Image


# ── Logger setup ─────────────────────────────────────────────────────────────

def get_logger(name: str = "ecomm_pipeline") -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger(name)


logger = get_logger()


# ── Directory helpers ─────────────────────────────────────────────────────────

def ensure_dir(path: str) -> Path:
    """Create directory if it does not exist. Returns Path object."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


# ── Image saving ──────────────────────────────────────────────────────────────

def save_image(image: Image.Image, output_dir: str, filename: str) -> str:
    """
    Save a PIL Image to disk.

    Args:
        image:      PIL Image object.
        output_dir: Target directory path.
        filename:   Output filename (without extension).

    Returns:
        Full path to the saved image.
    """
    out_dir = ensure_dir(output_dir)
    filepath = str(out_dir / f"{filename}.png")
    image.save(filepath)
    logger.info(f"Saved image → {filepath}")
    return filepath


def save_product_images(
    images: List[Image.Image],
    product: Dict,
    prompt_type: str,
    output_root: str,
) -> List[str]:
    """
    Save all seed-variant images for a single product.

    Naming convention: {asin}_{prompt_type}_seed{i}.png

    Args:
        images:      List of PIL Images (one per seed).
        product:     Product metadata dict.
        prompt_type: 'baseline' or 'structured'
        output_root: Root output directory (e.g. 'outputs/')

    Returns:
        List of saved file paths.
    """
    asin = product.get("asin", "unknown")
    out_dir = os.path.join(output_root, prompt_type)
    ensure_dir(out_dir)

    paths = []
    for i, img in enumerate(images):
        filename = f"{asin}_{prompt_type}_seed{i}"
        path = save_image(img, out_dir, filename)
        paths.append(path)
    return paths


# ── Comparison grid ───────────────────────────────────────────────────────────

def make_comparison_grid(
    baseline_paths: List[str],
    structured_paths: List[str],
    product_title: str,
    output_path: str,
    thumb_size: int = 300,
) -> str:
    """
    Create a side-by-side comparison grid image.

    Layout:
        Row 1 label: "BASELINE (naive prompt)"
        Row 2 label: "STRUCTURED prompt"
        Columns: up to 3 seed images per row

    Returns:
        Path to the saved grid image.
    """
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    n_cols = max(len(baseline_paths), len(structured_paths), 1)
    fig, axes = plt.subplots(2, n_cols, figsize=(n_cols * 4, 9))
    fig.suptitle(f"{product_title}\n", fontsize=13, fontweight="bold")

    row_labels = ["BASELINE\n(naive prompt)", "STRUCTURED\nprompt"]
    row_data   = [baseline_paths, structured_paths]

    for row_idx, (label, paths) in enumerate(zip(row_labels, row_data)):
        for col_idx in range(n_cols):
            ax = axes[row_idx][col_idx] if n_cols > 1 else axes[row_idx]
            ax.axis("off")
            if col_idx < len(paths) and os.path.exists(paths[col_idx]):
                img = mpimg.imread(paths[col_idx])
                ax.imshow(img)
                if col_idx == 0:
                    ax.set_ylabel(label, fontsize=11, rotation=0,
                                  labelpad=80, va="center")
            else:
                ax.text(0.5, 0.5, "N/A", ha="center", va="center",
                        transform=ax.transAxes, fontsize=10)

    plt.tight_layout()
    ensure_dir(os.path.dirname(output_path))
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close()
    logger.info(f"Comparison grid saved → {output_path}")
    return output_path


# ── Results logging ───────────────────────────────────────────────────────────

def save_results_json(results: List[Dict], output_path: str) -> None:
    """Save evaluation results list to a JSON file."""
    ensure_dir(os.path.dirname(output_path))
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved → {output_path}")


def timestamp() -> str:
    """Return a compact timestamp string for filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
