"""Shared Gemini AI client for ReMind."""

import os
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Global model instances
_models = {}


def get_gemini_model(model_name: str = "gemini-2.5-flash"):
    """
    Get or create a Gemini model instance (cached).

    Args:
        model_name: Model identifier (default: gemini-2.5-flash)

    Returns:
        genai.GenerativeModel: Configured Gemini model
    """
    global _models

    # Normalize model name
    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"

    if model_name not in _models:
        _models[model_name] = genai.GenerativeModel(model_name)

    return _models[model_name]


def generate_text(
    prompt: str,
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.7,
    max_tokens: int = 300
) -> str:
    """
    Generate text using Gemini with fallback to alternative models.

    Args:
        prompt: Input prompt
        model_name: Model to use (default: gemini-2.5-flash)
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum output tokens

    Returns:
        str: Generated text

    Raises:
        Exception: If all models fail
    """
    # Try different model names if primary fails
    model_names_to_try = [
        model_name,
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash"
    ]

    last_error = None

    for model_to_try in model_names_to_try:
        try:
            model = get_gemini_model(model_to_try)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )

            if response.candidates:
                return response.candidates[0].content.parts[0].text.strip()
            else:
                raise Exception("No response generated")

        except Exception as e:
            last_error = e
            continue

    # If all failed, raise the last error
    raise last_error if last_error else Exception("Failed to generate text")


def generate_memory_context(
    description: str,
    people: list = None,
    model_name: str = "gemini-2.5-flash"
) -> str:
    """
    Generate memory context description using Gemini.

    Args:
        description: Visual description of the memory
        people: List of people in the memory
        model_name: Model to use

    Returns:
        str: AI-generated context
    """
    people_str = ", ".join(people) if people else "unknown people"

    prompt = f"""Describe this memory in a warm, engaging way for someone with Alzheimer's:

Visual: {description}
People present: {people_str}

Create a brief (2-3 sentences), emotionally warm description that captures the essence of this moment."""

    return generate_text(prompt, model_name=model_name, temperature=0.8, max_tokens=200)
