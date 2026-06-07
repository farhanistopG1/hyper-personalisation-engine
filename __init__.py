"""
💀 HYPER PERSONALISATION N-ORGAN 💀

Pizza Express customer re-engagement AI system.

Responsibilities:
- AI-powered dish recommendations (DeepSeek)
- Personalized WhatsApp message generation
- Warm, friendly, professional tone
"""

__version__ = "1.0.0"

from .personalisation_norgan import PersonalisationNOrgan, PersonalisationGuardian
from .schemas import (
    PersonalisationRequest,
    PersonalisationResponse,
    PersonalisedMessage,
    CustomerInput,
    MenuItem
)

__all__ = [
    "PersonalisationNOrgan",
    "PersonalisationGuardian",
    "PersonalisationRequest",
    "PersonalisationResponse",
    "PersonalisedMessage",
    "CustomerInput",
    "MenuItem"
]
