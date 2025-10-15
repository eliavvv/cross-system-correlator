"""Cross-System Event Correlator module."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Event:
    """ """

    ts: datetime
    source: str
    actor: str
    action: str
    meta: Dict[str, Any] = field(default_factory=dict)

    def request_id(self) -> Optional[str]:
        """ """
        return (
            self.meta.get("request_id")
            or self.meta.get("triggered_by")
            or self.meta.get("parent_request")
        )
