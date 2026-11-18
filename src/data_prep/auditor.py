"""Raw Data Auditor module.
Computes MD5 hashes and file-level row counts for archive files without modifying raw contents.
"""
import hashlib
import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class FileAuditRecord:
    file_name: str
    file_path: str
    file_size_bytes: int
    row_count: int
    md5_hash: str

def compute_md5(file_path: str, chunk_size: int = 65536) -> str:
    """Compute the MD5 hexadecimal digest of a file."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def count_csv_rows(file_path: str) -> int:
    """Count data rows in a CSV file (excluding header)."""
    count = 0
    with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
        # Check if header exists
        header = f.readline()
        if not header:
            return 0
        for _ in f:
            count += 1
    return count

def audit_raw_directory(raw_dir: str) -> List[FileAuditRecord]:
    """Audit all CSV files in the raw dataset directory."""
    records: List[FileAuditRecord] = []
    if not os.path.isdir(raw_dir):
        return records

    for fname in sorted(os.listdir(raw_dir)):
        if fname.lower().endswith(".csv"):
            full_path = os.path.join(raw_dir, fname)
            size = os.path.getsize(full_path)
            md5_val = compute_md5(full_path)
            rows = count_csv_rows(full_path)
            records.append(FileAuditRecord(
                file_name=fname,
                file_path=full_path,
                file_size_bytes=size,
                row_count=rows,
                md5_hash=md5_val
            ))
    return records

def generate_audit_report(
    records: List[FileAuditRecord],
    clean_count: int,
    conflict_count_groups: int,
    conflict_count_rows: int,
    recovered_site_id_count: int,
    output_path: str
) -> str:
    """Generate Markdown cleaning and audit report."""
    total_raw_rows = sum(r.row_count for r in records)
    
    lines = [
        "# Taiwan MOENV AQI Historical Dataset (AQX_P_488) Cleaning Report",
        "",
        "## 1. Executive Summary",
        f"- **Audit Period**: 2026-01-01 to 2026-10-29",
        f"- **Raw CSV Files Audited**: {len(records)}",
        f"- **Total Raw Input Rows**: {total_raw_rows:,}",
        f"- **Valid Clean Observations**: {clean_count:,}",
        f"- **Isolated Conflict Groups**: {conflict_count_groups}",
        f"- **Total Conflicting / Unresolved Rows**: {conflict_count_rows}",
        f"- **Recovered SiteId Count**: {recovered_site_id_count}",
        "",
        "## 2. File-level Integrity & MD5 Checksums",
        "",
        "| File Name | File Size (Bytes) | Row Count | MD5 Checksum |",
        "| :--- | :--- | :--- | :--- |"
    ]

    for r in records:
        lines.append(f"| `{r.file_name}` | {r.file_size_bytes:,} | {r.row_count:,} | `{r.md5_hash}` |")

    lines.extend([
        "",
        "## 3. Data Cleaning & Integrity Policies Applied",
        "- **Sentinel Normalization**: `-`, `--`, `NA`, and blank strings converted to NULL/None.",
        "- **Primary Key Deduplication**: Grouped on `(SiteId, DataCreationDate)`. Identical observations safely merged.",
        "- **Conflict Isolation**: All variants with conflicting measurements excluded from clean dataset and logged.",
        "- **Spatial SiteId Recovery**: Missing `SiteId` filled ONLY when county and coordinates uniquely matched a known station.",
        "",
        "---",
        "*Report generated automatically by Taiwan Air Quality Evidence Agent pipeline.*"
    ])

    report_text = "\n".join(lines)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
        
    return report_text
