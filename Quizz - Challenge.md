CS 5542- Quiz Challenge (GenAI: Stable Diffusion)

Theme: Real-World Controlled Image Generation

Submission Deadline: April 20, 2026
Style: Individual
Submission: Canvas (PowerPoints)
Credit: 5%

Goal

This challenge is designed to help you understand how generative AI systems can be applied to real-world problems with control, structure, and measurable performance.

Challenge Overview

In this challenge, you will build a data-driven image generation system using Stable Diffusion for real-world applications. You must choose ONE of the following scenarios and develop a controlled, evaluated generation pipeline.

Scenario Options (Choose One)

Option 1: E-Commerce Product Image Generation

Problem: E-commerce platforms such as Amazon and Shopify increasingly rely on AI to generate product images from metadata.
Task: Build a system that:

• Takes product metadata (title, category, attributes)

• Generates high-quality product images

Suggested Datasets:

• Amazon Product Dataset: https://nijianmo.github.io/amazon/index

• DeepFashion: http://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html

Requirements:

• Generate multiple images per product

• Ensure consistency for the same product across different views or styles

• Compare naive prompts versus structured prompts

Option 2: Interior Design Generation

Problem: Companies like IKEA use AI to design and visualize interior spaces.
Task: Build a system that:

• Takes room descriptions and constraints

• Generates interior design images

Suggested Dataset:

• SUN RGB-D: https://rgbd.cs.princeton.edu/

Requirements:

• Generate multiple room designs under constraints

• Maintain style and layout consistency

• Compare different prompt strategies and controlled versus uncontrolled generation

Technical Requirements

Your system must include the following components.

1. Stable Diffusion Pipeline

Use frameworks such as Hugging Face Diffusers or Stable Diffusion models.
Example GitHub Resources (Reference Only):

• huggingface/diffusers

• lllyasviel/ControlNet

• CompVis/stable-diffusion

• invoke-ai/InvokeAI

You may adapt or extend these implementations, but your work must include your own design and analysis.

2. Control Mechanism (Required)

Include at least one of the following:

• Structured prompt templates

• Negative prompts

• Conditioning such as ControlNet

3. Data to Prompt Mapping

Convert structured data into prompts and clearly define your prompt generation strategy.

Evaluation

You must define and apply evaluation metrics such as:

• Prompt alignment

• Consistency

• Diversity

• Quality (qualitative and optional quantitative)

You must include:

• Baseline versus improved comparison

• Failure cases and analysis

Submission Requirements

1. PPT (Minimum 10 Slides)

Your slides must include:

1. Scenario description

2. Dataset

3. Methodology (Stable Diffusion pipeline, Prompt design, Control strategy)

4. Tools and technologies

5. Results (images)

6. Video and GitHub URLs

7. Evaluation

8. Findings and insights

9. Limitations

10. AI tools used (required disclosure)

2. Demo Video (1 to 2 Minutes)

Provide a short demo video showing:

• System overview

• Input (data or prompt)

• Generated outputs

• Key results or comparisons
The video should be concise and hosted online such as GitHub or YouTube.

3. GitHub Repository

Include:

• Code

• Instructions in a README

• Sample outputs

• Dataset description

• List of tools and libraries used

Use of AI Tools

You are allowed and encouraged to use AI tools for coding, system building, evaluation, video creation, and presentation generation.
Examples include:

• ChatGPT, GitHub Copilot, Runway ML, Canva

Requirement:
You must clearly document:

• Which tools were used

• How they were used

• What parts were generated or assisted
Transparency is required for full credit.

Bonus (Extra Credit Opportunities)

You may earn bonus points by extending your system to multimodal generation, such as:

• Video generation (turning images into short clips or animations)

• Speech or audio generation (narration describing generated scenes)

• Image-to-video or text-to-video pipelines

• Integration with multimodal AI systems (image, text, and audio)

Bonus Requirement:

• Clearly demonstrate the multimodal extension

• Explain how it enhances your system

• Provide examples and evaluation

Expected Contributions

Your work should demonstrate:

• Completion of a working pipeline

• Thoughtful evaluation

• Analytical insight such as:

	• Why certain prompts perform better

	• Limitations of diffusion models

	• Trade-offs between control and diversity

Evaluation Criteria

• Completion of system: 30 percent

• Quality of outputs: 20 percent

• Evaluation and analysis: 25 percent

• Technical design: 15 percent

• Clarity of presentation and demo: 10 percent

• Bonus (multimodal extension): additional credit

Important Notes:

• Do not submit only generated images without analysis

• Your system must include both control and evaluation

• Show both successful and failed cases

• Properly acknowledge any external tools or code used
