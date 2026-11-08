"""Fail-open wrapper that never fails silently.

A write gate must not block the main flow when the gate itself breaks. But
"the gate allowed everything" and "the gate never loaded" look identical in
logs, so the wrapper always logs the exception before allowing the write.
"""

import logging
from typing import Optional

from .config import MemoryHygieneConfig
from .gate import WriteVerdict, assess_write

_LOGGER = logging.getLogger("agent_memory_hygiene")


def safe_assess_write(
    text: Optional[str],
    cfg: Optional[MemoryHygieneConfig] = None,
    *,
    logger: Optional[logging.Logger] = None,
) -> WriteVerdict:
    """Assess a candidate memory, failing open and loud on internal errors.

    Returns the normal verdict when the gate works. When it raises, returns a
    permissive verdict with ``reason="fail_open"`` and logs a warning, so the
    failure is visible without blocking the caller.
    """
    log = logger if logger is not None else _LOGGER
    try:
        return assess_write(text, cfg)
    except Exception as exc:  # noqa: BLE001 - this is the fail-open boundary
        log.warning("memory hygiene gate failed open: %s", exc)
        return WriteVerdict(ok=True, reason="fail_open", rule="exception", metrics={})
