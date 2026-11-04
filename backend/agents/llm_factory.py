from typing import Literal, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from config import get_settings
from utils.llm_factory import build_chat_model


def get_llm(role: str = "extractor") -> BaseChatModel:
    """Return configured BaseChatModel for the specified pipeline role."""
    settings = get_settings()
    if role == "vision":
        provider = settings.LLM_PROVIDER_VISION
        model_name = settings.VISION_MODEL
    elif role == "judge":
        provider = settings.LLM_PROVIDER_JUDGE
        model_name = settings.JUDGE_MODEL
    elif role == "classifier":
        provider = settings.LLM_PROVIDER_VISION
        model_name = getattr(settings, "CLASSIFIER_MODEL", settings.VISION_MODEL)
    else:
        provider = settings.LLM_PROVIDER_EXTRACTOR
        model_name = settings.EXTRACTOR_MODEL

    return build_chat_model(
        provider=provider,
        model=model_name,
        settings=settings,
        temperature=0.0,
    )
