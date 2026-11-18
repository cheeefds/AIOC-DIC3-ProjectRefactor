"""MOENV Taiwan AQI Domain Rules and Sub-index Calculation.
Implements sub-index interpolation, overall AQI determination (max sub-index), and category mapping.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class SubIndexBreakpoint:
    i_low: int
    i_high: int
    c_low: float
    c_high: float

# Official MOENV AQI Breakpoints table
AQI_BREAKPOINTS = {
    "pm2_5": [
        SubIndexBreakpoint(0, 50, 0.0, 15.4),
        SubIndexBreakpoint(51, 100, 15.5, 35.4),
        SubIndexBreakpoint(101, 150, 35.5, 54.4),
        SubIndexBreakpoint(151, 200, 54.5, 150.4),
        SubIndexBreakpoint(201, 300, 150.5, 250.4),
        SubIndexBreakpoint(301, 400, 250.5, 350.4),
        SubIndexBreakpoint(401, 500, 350.5, 500.4),
    ],
    "pm10": [
        SubIndexBreakpoint(0, 50, 0.0, 54.0),
        SubIndexBreakpoint(51, 100, 55.0, 125.0),
        SubIndexBreakpoint(101, 150, 126.0, 254.0),
        SubIndexBreakpoint(151, 200, 255.0, 354.0),
        SubIndexBreakpoint(201, 300, 355.0, 424.0),
        SubIndexBreakpoint(301, 400, 425.0, 504.0),
        SubIndexBreakpoint(401, 500, 505.0, 604.0),
    ],
    "o3_8hr": [
        SubIndexBreakpoint(0, 50, 0.0, 0.054),
        SubIndexBreakpoint(51, 100, 0.055, 0.070),
        SubIndexBreakpoint(101, 150, 0.071, 0.085),
        SubIndexBreakpoint(151, 200, 0.086, 0.105),
        SubIndexBreakpoint(201, 300, 0.106, 0.200),
    ],
    "so2": [
        SubIndexBreakpoint(0, 50, 0.0, 35.0),
        SubIndexBreakpoint(51, 100, 36.0, 75.0),
        SubIndexBreakpoint(101, 150, 76.0, 185.0),
        SubIndexBreakpoint(151, 200, 186.0, 304.0),
        SubIndexBreakpoint(201, 300, 305.0, 604.0),
    ],
    "co_8hr": [
        SubIndexBreakpoint(0, 50, 0.0, 4.4),
        SubIndexBreakpoint(51, 100, 4.5, 9.4),
        SubIndexBreakpoint(101, 150, 9.5, 12.4),
        SubIndexBreakpoint(151, 200, 12.5, 15.4),
        SubIndexBreakpoint(201, 300, 15.5, 30.4),
    ],
    "no2": [
        SubIndexBreakpoint(0, 50, 0.0, 53.0),
        SubIndexBreakpoint(51, 100, 54.0, 100.0),
        SubIndexBreakpoint(101, 150, 101.0, 360.0),
        SubIndexBreakpoint(151, 200, 361.0, 649.0),
        SubIndexBreakpoint(201, 300, 650.0, 1249.0),
    ]
}

def get_aqi_category(aqi: int) -> Tuple[str, str, str]:
    """Return (CategoryName, ColorCode, HealthAdvice)."""
    if aqi <= 50:
        return "良好", "Green", "空氣品質良好，污染程度低或無污染。"
    elif aqi <= 100:
        return "普通", "Yellow", "空氣品質普通；但對極特殊敏感族群建議減少戶外劇烈活動。"
    elif aqi <= 150:
        return "對敏感族群不健康", "Orange", "敏感族群（如氣喘、心血管疾病、幼童與長者）應減少戶外劇烈活動。"
    elif aqi <= 200:
        return "對所有族群不健康", "Red", "所有民眾應減少戶外長時間劇烈活動；敏感族群建議留在室內。"
    elif aqi <= 300:
        return "非常不健康", "Purple", "所有民眾應減少戶外活動，敏感族群應留在室內並減少體力消耗。"
    else:
        return "危害", "Maroon", "所有民眾應避免所有戶外活動，留在室內並緊閉門窗。"

def compute_subindex(pollutant: str, conc: float) -> Optional[int]:
    """Calculate individual pollutant sub-index via linear interpolation."""
    key = pollutant.lower().replace(".", "_")
    breakpoints = AQI_BREAKPOINTS.get(key)
    if not breakpoints or conc is None or conc < 0:
        return None

    for bp in breakpoints:
        if bp.c_low <= conc <= bp.c_high:
            # Linear interpolation: Ip = (I_high - I_low) / (C_high - C_low) * (Cp - C_low) + I_low
            ip = ((bp.i_high - bp.i_low) / (bp.c_high - bp.c_low)) * (conc - bp.c_low) + bp.i_low
            return round(ip)

    # If exceeding highest breakpoint
    highest = breakpoints[-1]
    if conc > highest.c_high:
        return highest.i_high
    return None

@dataclass
class AQIVerificationResult:
    reported_aqi: Optional[int]
    calculated_aqi: Optional[int]
    reported_primary_pollutant: Optional[str]
    calculated_dominant_pollutant: Optional[str]
    is_aqi_consistent: bool
    sub_indices: Dict[str, int]
    category_name: str
    color_code: str
    health_advice: str
    discrepancy_warning: Optional[str]

def verify_aqi_and_dominant_pollutant(
    reported_aqi: Optional[int],
    reported_pollutant: Optional[str],
    measurements: Dict[str, Optional[float]]
) -> AQIVerificationResult:
    """Verify reported AQI against sub-indices according to MOENV rules.
    
    Overall station AQI must equal max(sub_indices).
    Dominant pollutant corresponds to the pollutant with the maximum sub-index.
    """
    sub_indices: Dict[str, int] = {}
    for pol in ["pm2_5", "pm10", "o3_8hr", "so2", "no2"]:
        conc = measurements.get(pol)
        if conc is not None:
            si = compute_subindex(pol, conc)
            if si is not None:
                sub_indices[pol] = si

    if not sub_indices:
        calc_aqi = reported_aqi
        dominant = reported_pollutant
    else:
        # Find pollutant with max sub-index
        dominant, calc_aqi = max(sub_indices.items(), key=lambda x: x[1])

    eval_aqi = reported_aqi if reported_aqi is not None else calc_aqi
    cat_name, color, advice = get_aqi_category(eval_aqi or 0)

    # Discrepancy check
    discrepancy = None
    is_consistent = True
    if reported_aqi is not None and calc_aqi is not None and abs(reported_aqi - calc_aqi) > 5:
        is_consistent = False
        discrepancy = (
            f"報告 AQI ({reported_aqi}) 與由副指標計算之 AQI ({calc_aqi}, 主導: {dominant}) 存在差距，"
            f"可能因環境部移動平均時窗更新時間差或個別副指標暫時缺漏所致。"
        )

    return AQIVerificationResult(
        reported_aqi=reported_aqi,
        calculated_aqi=calc_aqi,
        reported_primary_pollutant=reported_pollutant,
        calculated_dominant_pollutant=dominant,
        is_aqi_consistent=is_consistent,
        sub_indices=sub_indices,
        category_name=cat_name,
        color_code=color,
        health_advice=advice,
        discrepancy_warning=discrepancy
    )
