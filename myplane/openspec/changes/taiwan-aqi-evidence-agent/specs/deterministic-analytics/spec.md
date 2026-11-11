## ADDED Requirements

### Requirement: Deterministic Trend Calculation
The system SHALL compute chronological trend directions (increasing, decreasing, stable) and exact delta values for specified pollutants or AQI over the given time window using deterministic numerical code.

#### Scenario: Computing change between start and end observations
- **WHEN** user requests pollutant trend for a station across a valid multi-hour interval
- **THEN** system calculates the net difference, percentage change, and min/max values deterministically, outputting verifiable floating-point numbers

#### Scenario: Insufficient data points for trend
- **WHEN** fewer than two valid temporal data points exist in the requested interval
- **THEN** system outputs an explicit limitation warning stating that trend calculation cannot be performed due to insufficient observations

### Requirement: Station Comparison and Ranking
The system SHALL compare pollutant concentrations or AQI across multiple specified stations for an identical time period and rank them deterministically.

#### Scenario: Multi-station ranking
- **WHEN** user requests comparison of multiple stations (e.g., "台中 vs 彰化") over an identical time interval
- **THEN** system computes station-specific summary statistics (e.g., mean, maximum) and ranks stations in descending order of pollutant levels with exact numeric differences

#### Scenario: Temporal misalignment across stations
- **WHEN** candidate stations possess non-overlapping timestamps or uneven missingness within the requested window
- **THEN** system aligns stations strictly on shared valid timestamps or issues an explicit caveat regarding uneven coverage

### Requirement: Persistence Baseline Comparison
The system SHALL calculate a simple persistence baseline (value at $t_0$ maintained across the window) to benchmark any event or trend observation.

#### Scenario: Event observation against persistence baseline
- **WHEN** an event or significant change is evaluated
- **THEN** system outputs the persistence baseline alongside actual observed changes to highlight genuine deviation

