"""
pipeline.py
-----------
Stable Diffusion XL image generation pipeline.

Runs on Google Colab (T4/A100 GPU). Accepts a list of products,
generates 'num_seeds' images per product for both naive (baseline)
and structured prompts, and saves all outputs.
"""

import os
import torch
from typing import List, Dict, Optional
from pathlib import Path

from src.data_loader import load_products, get_valid_products
from src.prompt_builder import (
    build_naive_prompt,
    build_structured_prompt,
    build_negative_prompt,
)
from src.utils import save_product_images, get_logger, ensure_dir

logger = get_logger("pipeline")

# ── Default generation config ─────────────────────────────────────────────────
DEFAULT_CONFIG = {
    "model_id":           "stabilityai/stable-diffusion-xl-base-1.0",
    "num_inference_steps": 30,
    "guidance_scale":      7.5,
    "width":               1024,
    "height":              1024,
    "seeds":               [42, 123, 999],      # 3 seeds → 3 images per product
}


def load_pipeline(model_id: str, use_refiner: bool = False):
    """
    Load the SDXL pipeline onto GPU.

    Args:
        model_id:    HuggingFace model identifier.
        use_refiner: If True, also load the SDXL refiner for higher quality.

    Returns:
        Loaded diffusion pipeline (and optionally refiner).
    """
    from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline

    logger.info(f"Loading SDXL pipeline: {model_id}")
    pipe = StableDiffusionXLPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True,
    )
    pipe = pipe.to("cuda")
    pipe.enable_model_cpu_offload()   # Saves VRAM on T4 GPUs
    logger.info("Pipeline loaded on CUDA.")

    if use_refiner:
        refiner_id = "stabilityai/stable-diffusion-xl-refiner-1.0"
        logger.info(f"Loading SDXL refiner: {refiner_id}")
        refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained(
            refiner_id,
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True,
        )
        refiner = refiner.to("cuda")
        return pipe, refiner

    return pipe, None


def generate_images(
    pipe,
    prompt: str,
    negative_prompt: str,
    seeds: List[int],
    config: Dict,
    refiner=None,
):
    """
    Generate one image per seed for a given prompt.

    Args:
        pipe:            Loaded diffusion pipeline.
        prompt:          Positive prompt string.
        negative_prompt: Negative prompt string.
        seeds:           List of random seeds for reproducibility.
        config:          Generation config dict.
        refiner:         Optional SDXL refiner pipeline.

    Returns:
        List of PIL Image objects.
    """
    images = []
    for seed in seeds:
        generator = torch.Generator(device="cuda").manual_seed(seed)
        output = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=config["num_inference_steps"],
            guidance_scale=config["guidance_scale"],
            width=config["width"],
            height=config["height"],
            generator=generator,
            output_type="latent" if refiner else "pil",
        )

        if refiner:
            # Pass latents through refiner for sharper details
            refined = refiner(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=output.images,
                generator=generator,
            )
            images.append(refined.images[0])
        else:
            images.append(output.images[0])

    return images


def run_pipeline(
    products: List[Dict],
    output_root: str,
    config: Optional[Dict] = None,
    use_refiner: bool = False,
    max_products: Optional[int] = None,
) -> Dict[str, List[Dict]]:
    """
    Full pipeline: load model → loop products → generate baseline + structured.

    Args:
        products:     List of product dicts.
        output_root:  Root directory for saving images.
        config:       Generation config (uses DEFAULT_CONFIG if None).
        use_refiner:  Whether to use the SDXL refiner.
        max_products: Limit number of products (for quick tests).

    Returns:
        Dict with keys 'baseline' and 'structured', each a list of result dicts:
        {asin, title, prompt, image_paths}
    """
    if config is None:
        config = DEFAULT_CONFIG

    seeds          = config["seeds"]
    negative       = build_negative_prompt()
    pipe, refiner  = load_pipeline(config["model_id"], use_refiner)

    if max_products:
        products = products[:max_products]

    results = {"baseline": [], "structured": []}

    for i, product in enumerate(products):
        title = product.get("title", "unknown product")
        asin  = product.get("asin", f"product_{i}")
        logger.info(f"[{i+1}/{len(products)}] Processing: {title}")

        for prompt_type in ["baseline", "structured"]:
            if prompt_type == "baseline":
                prompt = build_naive_prompt(product)
            else:
                prompt = build_structured_prompt(product)

            logger.info(f"  [{prompt_type}] Prompt: {prompt[:80]}...")

            try:
                images = generate_images(
                    pipe=pipe,
                    prompt=prompt,
                    negative_prompt=negative,
                    seeds=seeds,
                    config=config,
                    refiner=refiner,
                )
                paths = save_product_images(images, product, prompt_type, output_root)
                results[prompt_type].append({
                    "asin":        asin,
                    "title":       title,
                    "prompt":      prompt,
                    "image_paths": paths,
                })
            except Exception as e:
                logger.error(f"  Failed to generate [{prompt_type}] for {asin}: {e}")
                results[prompt_type].append({
                    "asin":        asin,
                    "title":       title,
                    "prompt":      prompt,
                    "image_paths": [],
                    "error":       str(e),
                })

    logger.info("Pipeline complete.")
    return results


# ── CLI entrypoint (for local testing) ───────────────────────────────────────
if __name__ == "__main__":
    import sys
    from pathlib import Path

    root = Path(__file__).parent.parent
    data_path   = str(root / "data" / "sample_products.json")
    output_root = str(root / "outputs")

    products = load_products(data_path)
    products = get_valid_products(products)

    # Quick test: only 3 products, 2 seeds
    test_config = {**DEFAULT_CONFIG, "seeds": [42, 123], "num_inference_steps": 20}
    results = run_pipeline(
        products=products,
        output_root=output_root,
        config=test_config,
        max_products=3,
    )

    print(f"\nBaseline results:   {len(results['baseline'])} products")
    print(f"Structured results: {len(results['structured'])} products")
