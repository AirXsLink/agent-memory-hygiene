"""Write-time hygiene for agent memory: what to store, and whose fact it is."""

from .attribution import AttributionRisk, assess_attribution
from .config import MemoryHygieneConfig
from .fail_open import safe_assess_write
from .gate import WriteVerdict, assess_write, should_write

__version__ = "0.1.0"

__all__ = [
    "AttributionRisk",
    "MemoryHygieneConfig",
    "WriteVerdict",
    "assess_attribution",
    "assess_write",
    "safe_assess_write",
    "should_write",
]
