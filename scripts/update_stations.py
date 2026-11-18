import json
import csv
import re

with open('src/retrieval/station_catalog_extracted.json', encoding='utf-8') as f:
    raw_st = json.load(f)

# Extract English station names from clean dataset
en_names = {}
with open('data/processed/aqi_2026_clean.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        sid = int(r['site_id'])
        name = r['site_name']
        if not re.search('[\u4e00-\u9fa5]', name) and name.strip():
            en_names[sid] = name.strip()

lines = [
    '"""MOENV Taiwan Air Quality Monitoring Station Catalog and Metadata.',
    'Provides authoritative mapping for SiteId, SiteName (Chinese and English), County, coordinates, and SiteType.',
    '"""',
    'from dataclasses import dataclass',
    'from typing import Dict, List, Optional',
    '',
    '@dataclass(frozen=True)',
    'class StationMetadata:',
    '    site_id: int',
    '    site_name: str',
    '    site_eng_name: str',
    '    county: str',
    '    lon: float',
    '    lat: float',
    '    site_type: str = "一般空氣品質測站"',
    '',
    '# Exact MOENV AQX_P_488 88-Station Directory extracted from dataset',
    'TAIWAN_AQI_STATIONS: Dict[int, StationMetadata] = {'
]

for sid_str in sorted(raw_st.keys(), key=lambda x: int(x)):
    sid = int(sid_str)
    info = raw_st[sid_str]
    name = info['name']
    county = info['county']
    eng = en_names.get(sid, "")
    lon = float(info['lon']) if info['lon'] else 0.0
    lat = float(info['lat']) if info['lat'] else 0.0
    lines.append(f'    {sid}: StationMetadata({sid}, "{name}", "{eng}", "{county}", {lon}, {lat}),')

lines.extend([
    '}',
    '',
    'def get_station_by_id(site_id: int) -> Optional[StationMetadata]:',
    '    """Retrieve station metadata by SiteId."""',
    '    return TAIWAN_AQI_STATIONS.get(site_id)',
    '',
    'def get_all_stations() -> List[StationMetadata]:',
    '    """Return all known station metadata objects."""',
    '    return list(TAIWAN_AQI_STATIONS.values())'
])

with open('src/retrieval/stations.py', 'w', encoding='utf-8') as out:
    out.write('\n'.join(lines) + '\n')

print('Successfully updated src/retrieval/stations.py with Chinese and English names!')
