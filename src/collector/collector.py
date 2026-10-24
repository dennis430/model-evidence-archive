"""Executable collector. Uses synthetic fixtures for offline tests.
Live path checks for credentials and records PAUSED_ACCESS when absent.
Never invents historical observations.
"""
from __future__ import annotations
import json
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PANEL_PATH = Path("probes/panel_v1.json")

def load_panel() -> dict:
    return json.loads(PANEL_PATH.read_text())

def collect_offline_fixture() -> dict:
    """Quarantined synthetic response for testing only. Never treated as historical."""
    return {
        "probe_id": "p1_duplicate",
        "model": "synthetic-fixture",
        "response_text": "Under declared copy model, one independent observation.",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "method": "offline_fixture",
        "hash": hashlib.sha256(b"synthetic").hexdigest(),
        "is_historical": False,
        "notes": "Quarantined test fixture; not a real provider response.",
    }

def check_access() -> dict:
    """Report access status without making requests if no secrets."""
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))
    has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_google = bool(os.environ.get("GOOGLE_API_KEY"))
    return {
        "openai": "AVAILABLE" if has_openai else "MISSING_SECRET",
        "anthropic": "AVAILABLE" if has_anthropic else "MISSING_SECRET",
        "google": "AVAILABLE" if has_google else "MISSING_SECRET",
        "overall": "PAUSED_ACCESS" if not (has_openai or has_anthropic or has_google) else "PARTIAL",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

def run_collection(dry_run: bool = True) -> dict:
    panel = load_panel()
    access = check_access()
    results = []
    if dry_run or access["overall"] == "PAUSED_ACCESS":
        results.append(collect_offline_fixture())
        return {
            "panel_version": panel.get("version"),
            "access": access,
            "results": results,
            "note": "No live provider calls made. Offline fixture only for testing.",
        }
    return {"access": access, "results": [], "note": "Live adapters not invoked without credentials."}
