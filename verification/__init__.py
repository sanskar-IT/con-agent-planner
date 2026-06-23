"""Verification and source provenance module."""
from verification.source_verifier import (
    SourceTier,
    SourceRecord,
    verify_claim,
    format_confidence_label,
    is_trusted,
    TRUST_THRESHOLDS,
)
