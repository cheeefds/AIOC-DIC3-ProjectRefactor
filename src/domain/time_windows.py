"""Time Semantics and Averaging Windows for MOENV AQI Pollutants.
Provides regulatory averaging window specifications, unit declarations, and Taiwan Time (UTC+8) tags.
"""
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass(frozen=True)
class PollutantSpec:
    code: str
    display_name: str
    unit: str
    averaging_window: str
    regulatory_basis: str
    description: str

POLLUTANT_SPECS: Dict[str, PollutantSpec] = {
    "aqi": PollutantSpec(
        code="aqi",
        display_name="空氣品質指標 (AQI)",
        unit="無單位 (指標值 0-500)",
        averaging_window="依當小時各污染物法定移動平均副指標之最大值判定",
        regulatory_basis="環境部空氣品質指標 (AQI) 規範",
        description="綜合性指標，數值由各污染物副指標之最大者決定。"
    ),
    "pm2_5": PollutantSpec(
        code="pm2_5",
        display_name="細懸浮微粒 (PM2.5)",
        unit="μg/m³",
        averaging_window="12小時/4小時加權移動平均 (0.5 * 前12hr平均 + 0.5 * 前4hr平均)",
        regulatory_basis="空氣品質標準第 3 條及 AQI 計算規則",
        description="逐時發布之 PM2.5 數值為加權移動平均，非瞬間單點濃度。"
    ),
    "pm10": PollutantSpec(
        code="pm10",
        display_name="懸浮微粒 (PM10)",
        unit="μg/m³",
        averaging_window="24小時移動平均",
        regulatory_basis="空氣品質標準第 3 條",
        description="採 24 小時移動平均以反映中長期暴露。"
    ),
    "o3": PollutantSpec(
        code="o3",
        display_name="臭氧 (O3)",
        unit="ppm",
        averaging_window="1小時平均",
        regulatory_basis="環境部逐時觀測",
        description="當小時之單小時平均濃度。"
    ),
    "o3_8hr": PollutantSpec(
        code="o3_8hr",
        display_name="臭氧 (O3) 8小時移動平均",
        unit="ppm",
        averaging_window="前8小時移動平均",
        regulatory_basis="AQI 臭氧副指標計算標準",
        description="臭氧 AQI 副指標主要依據 8 小時移動平均判定。"
    ),
    "co": PollutantSpec(
        code="co",
        display_name="一氧化碳 (CO)",
        unit="ppm",
        averaging_window="8小時移動平均",
        regulatory_basis="空氣品質標準及 AQI 計算規則",
        description="採 8 小時移動平均計算副指標。"
    ),
    "so2": PollutantSpec(
        code="so2",
        display_name="二氧化硫 (SO2)",
        unit="ppb",
        averaging_window="1小時平均",
        regulatory_basis="空氣品質標準第 3 條",
        description="採當小時 1 小時平均值。"
    ),
    "no2": PollutantSpec(
        code="no2",
        display_name="二氧化氮 (NO2)",
        unit="ppb",
        averaging_window="1小時平均",
        regulatory_basis="空氣品質標準第 3 條",
        description="採當小時 1 小時平均值。"
    ),
}

def get_pollutant_spec(pollutant_code: str) -> Optional[PollutantSpec]:
    """Retrieve pollutant specification by canonical name."""
    clean = pollutant_code.lower().replace(".", "_")
    return POLLUTANT_SPECS.get(clean)

def format_taiwan_time(dt_str: str) -> str:
    """Format timestamp explicitly marked as Taiwan Time (UTC+8)."""
    if not dt_str:
        return "未知時間"
    return f"{dt_str} (台灣時間, UTC+8)"

def get_regulatory_caveat(pollutant_code: str) -> str:
    """Generate regulatory moving-window caveat for specified pollutant."""
    spec = get_pollutant_spec(pollutant_code)
    if not spec:
        return "時間語意提醒：環境部資料發布時間採用台灣時間 (UTC+8)。"
    return (
        f"【法定平均時窗說明】{spec.display_name} 測定單位為 {spec.unit}，"
        f"其計算時窗為「{spec.averaging_window}」。"
        f"逐時觀測反映的是滑動平均視窗之整合結果，不應視為當下瞬間之極端峰值。"
    )
