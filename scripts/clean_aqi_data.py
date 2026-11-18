#!/usr/bin/env python3
"""Data cleaning pipeline for Taiwan MOENV AQI dataset (AQX_P_488).
Standard-library based, fully reproducible, strictly obeying OpenSpec and DESIGN.md.
"""
import argparse
import csv
import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data_prep.auditor import audit_raw_directory, generate_audit_report
from src.data_prep.normalizer import normalize_row
from src.data_prep.spatial_recovery import recover_site_id
from src.data_prep.deduplicator import process_observations

OUTPUT_FIELDNAMES = [
    "site_id", "site_name", "county", "aqi", "pollutant", "status",
    "so2", "co", "o3", "o3_8hr", "pm10", "pm2_5", "no2", "nox", "no",
    "wind_speed", "wind_direction", "data_creation_date", "lon", "lat",
    "source_file"
]

CONFLICT_FIELDNAMES = OUTPUT_FIELDNAMES + ["conflict_reason"]

def run_cleaning_pipeline(raw_dir: str, processed_dir: str) -> None:
    print(f"=== Starting Taiwan AQI Data Cleaning Pipeline ===")
    print(f"Input Raw Directory: {raw_dir}")
    print(f"Output Processed Directory: {processed_dir}")

    # Step 1: Raw data audit
    print("\n[Step 1/4] Auditing raw files and calculating MD5 checksums...")
    audit_records = audit_raw_directory(raw_dir)
    print(f"Found {len(audit_records)} raw CSV archive files.")

    all_normalized_rows = []
    recovered_site_id_count = 0

    # Step 2: Read, normalize, spatial recovery
    print("\n[Step 2/4] Reading, normalizing sentinels, and recovering SiteIds...")
    for rec in audit_records:
        with open(rec.file_path, "r", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                norm = normalize_row(row)
                norm["source_file"] = rec.file_name

                # Check if SiteId is missing and attempt recovery
                if norm.get("site_id") is None:
                    recovered_id, msg = recover_site_id(
                        norm.get("county"), norm.get("lon"), norm.get("lat")
                    )
                    if recovered_id is not None:
                        norm["site_id"] = recovered_id
                        recovered_site_id_count += 1
                    else:
                        norm["recovery_status"] = msg

                all_normalized_rows.append(norm)

    print(f"Parsed {len(all_normalized_rows):,} rows. Recovered SiteIds for {recovered_site_id_count} rows.")

    # Step 3: Deduplication and conflict isolation
    print("\n[Step 3/4] Grouping by (SiteId, DataCreationDate), merging duplicates, and isolating conflicts...")
    dedup_result = process_observations(all_normalized_rows)
    dedup_result.recovered_site_id_count = recovered_site_id_count

    print(f"Result summary:")
    print(f" - Clean observations: {len(dedup_result.clean_records):,}")
    print(f" - Conflict groups: {dedup_result.conflict_count_groups}")
    print(f" - Conflicting / invalid rows isolated: {dedup_result.conflict_count_rows}")
    print(f" - Non-conflicting rows merged: {dedup_result.merged_rows_count:,}")

    # Step 4: Write output files
    print("\n[Step 4/4] Writing clean dataset, conflict repository, and report...")
    os.makedirs(processed_dir, exist_ok=True)
    clean_csv_path = os.path.join(processed_dir, "aqi_2026_clean.csv")
    conflict_csv_path = os.path.join(processed_dir, "aqi_2026_conflicts.csv")
    report_md_path = os.path.join(processed_dir, "cleaning_report.md")

    # Write clean CSV
    with open(clean_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(dedup_result.clean_records)
    print(f"Wrote clean CSV to: {clean_csv_path}")

    # Write conflicts CSV
    with open(conflict_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CONFLICT_FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(dedup_result.conflict_records)
    print(f"Wrote conflicts CSV to: {conflict_csv_path}")

    # Generate Markdown Report
    generate_audit_report(
        records=audit_records,
        clean_count=len(dedup_result.clean_records),
        conflict_count_groups=dedup_result.conflict_count_groups,
        conflict_count_rows=dedup_result.conflict_count_rows,
        recovered_site_id_count=recovered_site_id_count,
        output_path=report_md_path
    )
    print(f"Wrote audit report to: {report_md_path}")
    print("\n=== Data Cleaning Pipeline Finished Successfully ===")

def main():
    parser = argparse.ArgumentParser(description="Clean and validate MOENV AQX_P_488 dataset.")
    parser.add_argument(
        "--raw-dir",
        default=os.path.join(PROJECT_ROOT, "data", "raw", "AQX_P_488_Resource"),
        help="Path to raw CSV files."
    )
    parser.add_argument(
        "--processed-dir",
        default=os.path.join(PROJECT_ROOT, "data", "processed"),
        help="Path to write processed artifacts."
    )
    args = parser.parse_args()
    run_cleaning_pipeline(args.raw_dir, args.processed_dir)

if __name__ == "__main__":
    main()
