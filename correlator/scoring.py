"""Cross-System Event Correlator module."""

from __future__ import annotations

import re
from typing import List

from .models import Event


def tokenize(s: str) -> set:
    """

    Args:
      s: str:
      s: str:
      s: str:

    Returns:

    """
    s = s.lower()
    return set(re.findall(r"[a-z0-9]+", s))


def time_bonus(delta_sec: float) -> float:
    """

    Args:
      delta_sec: float:
      delta_sec: float:
      delta_sec: float:

    Returns:

    """
    if delta_sec <= 5:
        return 0.30
    if delta_sec <= 20:
        return 0.20
    if delta_sec <= 60:
        return 0.10
    return 0.0


def endpoint_actor_hint(endpoint: str, actor: str) -> float:
    """

    Args:
      endpoint: str:
      actor: str:
      endpoint: str:
      actor: str:
      endpoint: str:
      actor: str:

    Returns:

    """
    hints = {
        "/reports/generate": {"job_svc", "export_svc"},
        "/export": {"export_svc"},
        "/backup/create": {"backup_svc"},
        "/analytics/run": {"analytics_svc"},
        "/metrics/daily": {"metrics_svc"},
        "/notifications/send": {"notification_svc"},
        "/audit/export": {"audit_svc"},
        "/dashboard/stats": {"dashboard_svc"},
        "/sync/external": {"sync_svc"},
        "/import/data": {"import_svc"},
        "/cleanup/temp": {"cleanup_svc"},
        "/data/customers": {"api_svc"},
        "/data/orders": {"api_svc"},
        "/admin/users": {"admin_svc"},
    }
    for key, actors in hints.items():
        if key in endpoint and actor in actors:
            return 0.10
    return 0.0


def similarity_bonus(a: str, b: str) -> float:
    """

    Args:
      a: str:
      b: str:
      a: str:
      b: str:
      a: str:
      b: str:

    Returns:

    """
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb:
        return 0.0
    overlap = len(ta & tb) / max(len(ta), len(tb))
    if overlap >= 0.4:
        return 0.20
    if overlap >= 0.2:
        return 0.10
    return 0.0


def score_link(prev: Event, nxt: Event) -> float:
    """

    Args:
      prev: Event:
      nxt: Event:
      prev: Event:
      nxt: Event:
      prev: Event:
      nxt: Event:

    Returns:

    """
    score = 0.0
    rid_prev = prev.request_id()
    rid_next = nxt.request_id()
    if rid_prev and rid_next and rid_prev == rid_next:
        score += 1.0
    delta_sec = abs((nxt.ts - prev.ts).total_seconds())
    score += time_bonus(delta_sec)
    score += similarity_bonus(prev.action, nxt.action)
    if prev.actor == nxt.actor and prev.actor:
        score += 0.20
    if prev.source == "API":
        parts = prev.action.split()
        endpoint = parts[-1] if parts else ""
        score += endpoint_actor_hint(endpoint, nxt.actor)
    return score


def confidence(score: float) -> str:
    """

    Args:
      score: float:
      score: float:
      score: float:

    Returns:

    """
    if score >= 1.0:
        return "HIGH"
    if score >= 0.5:
        return "MEDIUM"
    return "LOW"
