"""Evidence Guard module.
Cross-references every numerical claim in agent response drafts against retrieved data and analytics findings.
Blocks or qualifies hallucinated and unsupported claims.
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

@dataclass
class VerifiedClaim:
    claim_text: str
    station_name: str
    site_id: int
    timestamp: str
    record_key: str
    pollutant: str
    value: float

@dataclass
class EvidenceGuardResult:
    is_fully_supported: bool
    verified_numbers_count: int
    unsupported_numbers_count: int
    provenance_fidelity: float  # Supported / Total numbers
    unsupported_values: List[float]
    sanitized_text: str
    guard_logs: List[str] = field(default_factory=list)

# Standard numbers permitted in prose (years, standard hours, weights, AQI breakpoints, tolerances)
STANDARD_ALLOWED_NUMBERS: Set[float] = {
    2026.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 24.0,
    0.0, 0.5, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 100.0
}

def extract_numbers_from_text(text: str) -> List[Tuple[float, str]]:
    """Extract all numeric occurrences (integers, floats, percentages) from text."""
    # Matches integers and floats, handles optional % sign
    pattern = r"(?<![A-Za-z0-9_])[-+]?\d+(?:\.\d+)?%?"
    matches = re.finditer(pattern, text)
    extracted: List[Tuple[float, str]] = []
    
    for m in matches:
        raw_token = m.group(0)
        # Skip markdown bullet numbers like "1." at start of line
        start_pos = m.start()
        if start_pos == 0 or text[start_pos-1] == '\n':
            if m.end() < len(text) and text[m.end()] == '.':
                continue

        clean_token = raw_token.replace("%", "").strip()
        try:
            val = float(clean_token)
            extracted.append((val, raw_token))
        except ValueError:
            continue
            
    return extracted

def verify_response_evidence(
    text: str,
    known_numeric_values: Set[float],
    known_site_ids: Set[int],
    tolerance: float = 0.05
) -> EvidenceGuardResult:
    """Verify that every number cited in text is grounded in known deterministic data."""
    extracted = extract_numbers_from_text(text)
    
    # Combined ground truth set
    valid_numbers = set(known_numeric_values)
    valid_numbers.update(float(sid) for sid in known_site_ids)
    valid_numbers.update(STANDARD_ALLOWED_NUMBERS)

    supported_count = 0
    unsupported_values: List[float] = []
    guard_logs: List[str] = []
    sanitized = text

    for val, raw_str in extracted:
        is_matched = False
        for target in valid_numbers:
            if abs(val - target) <= tolerance:
                is_matched = True
                break

        if is_matched:
            supported_count += 1
        else:
            unsupported_values.append(val)
            guard_logs.append(f"UNSUPPORTED_NUMERIC_CLAIM: 文本中出現未經驗證之數值 {val} (字串: '{raw_str}')")
            # Annotate unsupported claim in text
            sanitized = sanitized.replace(raw_str, f"{raw_str} [⚠️此數值缺乏原始觀測證據支持]")

    total = len(extracted)
    fidelity = round(supported_count / max(total, 1), 4)
    is_fully_supported = len(unsupported_values) == 0

    return EvidenceGuardResult(
        is_fully_supported=is_fully_supported,
        verified_numbers_count=supported_count,
        unsupported_numbers_count=len(unsupported_values),
        provenance_fidelity=fidelity,
        unsupported_values=unsupported_values,
        sanitized_text=sanitized if not is_fully_supported else text,
        guard_logs=guard_logs
    )
