"""Cross-System Event Correlator module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .models import Event
from .scoring import confidence, score_link


@dataclass
class Chain:
    """ """

    key: str
    initiator: Optional[str]
    events: List[Event] = field(default_factory=list)
    score: float = 0.0


def build_chains(events: List[Event], window_sec: int = 60):
    """

    Args:
      events: List[Event]:
      window_sec: int:  (Default value = 60)
      events: List[Event]:
      window_sec: int:  (Default value = 60)
      events: List[Event]:
      window_sec: int:  (Default value = 60)

    Returns:

    """
    by_rid: Dict[str, Chain] = {}
    orphans: List[Event] = []
    for e in sorted(events, key=lambda x: x.ts):
        rid = e.request_id()
        if rid:
            ch = by_rid.get(rid)
            if not ch:
                initiator = e.actor if e.source == "API" else None
                ch = Chain(key=rid, initiator=initiator, events=[e])
                by_rid[rid] = ch
            else:
                ch.events.append(e)
                if ch.initiator is None and e.source == "API":
                    ch.initiator = e.actor
        else:
            orphans.append(e)
    unattached: List[Event] = []
    for e in orphans:
        best_key = None
        best_score = 0.0
        for key, ch in by_rid.items():
            last = ch.events[-1]
            s = score_link(last, e)
            if s > best_score:
                best_score = s
                best_key = key
        if best_key and best_score >= 0.5:
            by_rid[best_key].events.append(e)
            by_rid[best_key].score = max(by_rid[best_key].score, best_score)
        else:
            unattached.append(e)
    for ch in by_rid.values():
        total = 0.0
        pairs = 0
        for i in range(1, len(ch.events)):
            total += score_link(ch.events[i - 1], ch.events[i])
            pairs += 1
        ch.score = total / pairs if pairs else 0.0
    chains = sorted(by_rid.values(), key=lambda c: c.events[0].ts)
    return chains, unattached


def format_text(chains: List[Chain]) -> str:
    """

    Args:
      chains: List[Chain]:
      chains: List[Chain]:
      chains: List[Chain]:

    Returns:

    """
    lines: List[str] = []
    for ch in chains:
        conf = confidence(ch.score)
        initiator = ch.initiator or (ch.events[0].actor if ch.events else "?")
        lines.append(f"Chain: {ch.key} (initiated by {initiator})")
        for e in ch.events:
            hhmmss = e.ts.strftime("%H:%M:%S")
            extra = ""
            if e.source == "DB" and "rows" in e.meta:
                extra = f" ({e.meta['rows']} rows)"
            if e.source == "STORAGE" and "size_kb" in e.meta:
                extra = f" ({e.meta['size_kb']} KB)"
            lines.append(
                f"  [{hhmmss}] {e.source:<7}| {e.actor:<10}| {e.action}{extra}"
            )
        lines.append(f"\nCorrelation: {conf} (avg score {ch.score:.2f})\n")
    return "\n".join(lines)


def format_json(chains: List[Chain]) -> List[Dict[str, Any]]:
    """

    Args:
      chains: List[Chain]:
      chains: List[Chain]:
      chains: List[Chain]:

    Returns:

    """
    out = []
    for ch in chains:
        out.append(
            {
                "chain": ch.key,
                "initiator": ch.initiator,
                "confidence": confidence(ch.score),
                "avg_score": round(ch.score, 2),
                "events": [
                    {
                        "timestamp": e.ts.isoformat(),
                        "source": e.source,
                        "actor": e.actor,
                        "action": e.action,
                        "meta": e.meta,
                    }
                    for e in ch.events
                ],
            }
        )
    return out
