## ADDED Requirements

### Requirement: Location and Station Resolution
The system SHALL resolve user-specified place names, county names, or station names into a canonical set of MOENV `SiteId` integers using an explicit station mapping dictionary.

#### Scenario: Valid station name resolution
- **WHEN** user query specifies a recognized station name or county (e.g., "台中測站" or "西屯")
- **THEN** system maps the name to its corresponding canonical `SiteId` and displays the resolved station metadata

#### Scenario: Ambiguous or unknown location
- **WHEN** user query specifies an unrecognized location or a location with multiple plausible stations without specifying which
- **THEN** system requests clarification or lists available candidate stations with their respective `SiteId` values

### Requirement: Time Window Filtering and Provenance Retention
The system SHALL filter cleaned AQX_P_488 observations by the resolved `SiteId` list and requested time range, maintaining source archive provenance (source file and observation key) for every retrieved row.

#### Scenario: Valid time window retrieval
- **WHEN** a structured query with valid `SiteId` and time window `[T_start, T_end]` is submitted
- **THEN** system returns all matching records sorted chronologically, attaching source filename and line key to the retrieved dataset

#### Scenario: No records found in time window
- **WHEN** retrieval query matches no records in the specified period
- **THEN** system returns an empty result set alongside a provenance log explicitly declaring data absence for that period

