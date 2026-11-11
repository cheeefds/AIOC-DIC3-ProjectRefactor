## ADDED Requirements

### Requirement: Structured Planning and Intent Parsing
The system SHALL parse natural language queries into structured parameters containing intent type (trend, station comparison, AQI interpretation, or out-of-scope), location targets, time window, and target pollutants.

#### Scenario: Parse answerable query
- **WHEN** user inputs "請問台中西屯站今天上午 PM2.5 趨勢如何？"
- **THEN** planner extracts `intent="trend"`, `location="西屯"`, `period="today morning"`, `pollutant="PM2.5"` and triggers data retrieval

#### Scenario: Identify unsupported request
- **WHEN** user inputs an unanswerable or speculative query (e.g., "是隔壁鋼鐵廠排放造成我今天過敏嗎？")
- **THEN** planner classifies the intent as out-of-scope / causal inquiry and routes to a standard policy limitation response

### Requirement: Evidence Guard Claim Verification
The system SHALL verify every numerical claim in the generated output against the deterministic execution results before delivering the response to the user.

#### Scenario: Validated claims delivered with provenance
- **WHEN** agent generates candidate statements mentioning specific values, stations, and times
- **THEN** Evidence Guard verifies that all numbers match retrieved records and attaches citation metadata `(Station, Time, RecordKey)` to each claim

#### Scenario: Interception of hallucinated or unsupported claims
- **WHEN** agent candidate text contains a numerical value or ranking not found in the deterministic analytics output
- **THEN** Evidence Guard strips or re-generates the unsupported sentence and flags the discrepancy in the system log

### Requirement: Uncertainty and Data Limitation Transparency
The system SHALL explicitly declare data gaps, timestamp missingness, conflict exclusions, or partial coverage in the final response.

#### Scenario: Response with partial data coverage
- **WHEN** the requested time window contains missing observation hours in the cleaned dataset
- **THEN** system includes an explicit limitation banner stating the missing hours and degree of temporal coverage

