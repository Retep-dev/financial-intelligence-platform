from openai import OpenAI

from core.config.settings import settings


def get_generation_client() -> OpenAI:
    """Return an OpenAI-compatible client for the configured generation provider."""
    provider = settings.GENERATION_PROVIDER.lower()

    if provider == "openai":
        return OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )

    if provider == "nvidia":
        return OpenAI(
            api_key=settings.NVIDIA_API_KEY,
            base_url=settings.NVIDIA_BASE_URL
        )

    raise ValueError(f"Unsupported generation provider: {settings.GENERATION_PROVIDER}")


def get_generation_model() -> str:
    provider = settings.GENERATION_PROVIDER.lower()

    if provider == "openai":
        return settings.OPENAI_GENERATION_MODEL

    if provider == "nvidia":
        return settings.NVIDIA_GENERATION_MODEL

    raise ValueError(f"Unsupported generation provider: {settings.GENERATION_PROVIDER}")


def generate_text(system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
    """Generate text using the configured provider."""
    client = get_generation_client()
    model = get_generation_model()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature
    )

    return response.choices[0].message.content.strip()
