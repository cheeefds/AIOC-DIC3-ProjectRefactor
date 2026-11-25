## ADDED Requirements

### Requirement: Raw Data Audit and Checksum Verification
The system SHALL verify the integrity of downloaded MOENV AQX_P_488 monthly archive CSV files by computing and logging MD5 checksums and file-level row counts before executing any data cleaning.

#### Scenario: Verify archive files
- **WHEN** raw CSV files are placed in `data/raw/AQX_P_488_Resource/` and data preparation is triggered
- **THEN** system computes MD5 checksums for all raw files and records them in `data/processed/cleaning_report.md` without modifying raw files

### Requirement: Sentinel Normalization
The system SHALL normalize missing-value sentinels (`-`, `--`, `NA`, and blank strings) in all pollutant and meteorological fields to standard empty representations (NULL/None).

#### Scenario: Handling sentinel characters
- **WHEN** raw CSV rows contain `-`, `--`, or `NA` in numeric pollutant columns
- **THEN** system replaces these values with null/empty values and preserves valid numeric strings

### Requirement: Deduplication and Conflict Isolation
The system SHALL use `(SiteId, DataCreationDate)` as the primary observation key. For duplicate rows with identical keys, the system SHALL merge them if non-missing values are consistent, and SHALL isolate all conflicting variants into a separate conflict repository if any numeric measurements disagree.

#### Scenario: Merging non-conflicting duplicates
- **WHEN** multiple rows have the same `(SiteId, DataCreationDate)` and their non-empty numeric fields agree completely
- **THEN** system merges them into a single clean observation, filling any empty cells from complement rows

#### Scenario: Isolating conflicting duplicates
- **WHEN** multiple rows share the same `(SiteId, DataCreationDate)` but differ in any non-empty numeric pollutant value
- **THEN** system excludes all conflicting variants from the clean dataset, appends them to `data/processed/aqi_2026_conflicts.csv`, and records the conflicting field names in the cleaning report

### Requirement: Spatial SiteId Recovery
The system SHALL attempt recovery for rows missing `SiteId` ONLY when county and exact geographic coordinates `(TWD97Lon, TWD97Lat)` uniquely match exactly one known station ID.

#### Scenario: Deterministic SiteId recovery
- **WHEN** a row has missing `SiteId` but its county and coordinate pair matches a single unique station in the known station catalog
- **THEN** system populates `SiteId` with the resolved ID and logs the recovery event

#### Scenario: Ambiguous SiteId recovery failure
- **WHEN** a row has missing `SiteId` and its county/coordinates do not uniquely identify a single station
- **THEN** system refuses to guess `SiteId` and moves the row to the conflict/unresolved log

