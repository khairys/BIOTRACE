"""Versioned parameters; R-* domain functions receive config explicitly."""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field

from biotrace_core.models import Model

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES = Path(__file__).parent / "rules" / "rules_r0.2.yaml"


class NamingConfig(Model):
    min_query_coverage: float = Field(ge=0, le=1)
    hit_window_pct: float = Field(ge=0)
    unknown_below_pct: float
    species_min_pct: float
    congener_gap_policy: Literal["strict", "threshold"]


class ScoringConfig(Model):
    l1_high_pct: float
    l1_high_gap: float
    l1_mid_pct: float
    l1_mid_gap: float
    l1_penalty_ref_fraction_below: float
    l4_full: float
    l4_partial: float
    l4_single_replicate_score: int
    min_total_reads: int
    grade_map: dict[int, str]


class RulesConfig(Model):
    rules_version: str
    status: str
    marker_default: str
    naming: NamingConfig
    scoring: ScoringConfig
    causes: dict[str, float]
    preprocess: dict[str, float]
    reference: dict[str, list[str]]
    validation: dict[str, float]
    curation: dict[str, str | int | float]
    priorities: dict[str, int]
    blast: dict[str, str | int | float]
    interpretation_limit: str


def load_rules(path: Path = DEFAULT_RULES) -> RulesConfig:
    return RulesConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def load_reasons() -> dict[str, dict[str, str]]:
    return yaml.safe_load((DEFAULT_RULES.parent / "reasons_r0.1.yaml").read_text(encoding="utf-8"))
