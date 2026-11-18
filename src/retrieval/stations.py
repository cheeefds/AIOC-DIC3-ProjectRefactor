"""MOENV Taiwan Air Quality Monitoring Station Catalog and Metadata.
Provides authoritative mapping for SiteId, SiteName (Chinese and English), County, coordinates, and SiteType.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass(frozen=True)
class StationMetadata:
    site_id: int
    site_name: str
    site_eng_name: str
    county: str
    lon: float
    lat: float
    site_type: str = "一般空氣品質測站"

# Exact MOENV AQX_P_488 88-Station Directory extracted from dataset
TAIWAN_AQI_STATIONS: Dict[int, StationMetadata] = {
    1: StationMetadata(1, "基隆", "Keelung", "基隆市", 121.760056, 25.129167),
    2: StationMetadata(2, "汐止", "Xizhi", "新北市", 121.64081, 25.06624),
    4: StationMetadata(4, "新店", "Xindian", "新北市", 121.537778, 24.977222),
    5: StationMetadata(5, "土城", "Tucheng", "新北市", 121.451861, 24.982528),
    6: StationMetadata(6, "板橋", "Banqiao", "新北市", 121.458667, 25.012972),
    7: StationMetadata(7, "新莊", "Xinzhuang", "新北市", 121.4325, 25.037972),
    8: StationMetadata(8, "菜寮", "Cailiao", "新北市", 121.481028, 25.06895),
    9: StationMetadata(9, "林口", "Linkou", "新北市", 121.36548982, 25.07798949),
    10: StationMetadata(10, "淡水", "Tamsui", "新北市", 121.449239, 25.1645),
    11: StationMetadata(11, "士林", "Shilin", "臺北市", 121.51666356, 25.10334003),
    12: StationMetadata(12, "中山", "Zhongshan", "臺北市", 121.526528, 25.062361),
    13: StationMetadata(13, "萬華", "Wanhua", "臺北市", 121.507972, 25.046503),
    14: StationMetadata(14, "古亭", "Guting", "臺北市", 121.529556, 25.020608),
    15: StationMetadata(15, "松山", "Songshan", "臺北市", 121.578611, 25.05),
    16: StationMetadata(16, "大同", "Datong", "臺北市", 121.51342074, 25.06331455),
    17: StationMetadata(17, "桃園", "Taoyuan", "桃園市", 121.30500531, 24.9947107),
    18: StationMetadata(18, "大園", "Dayuan", "桃園市", 121.20251473, 25.06100357),
    19: StationMetadata(19, "觀音", "Guanyin", "桃園市", 121.08283092, 25.03556747),
    20: StationMetadata(20, "平鎮", "Pingzhen", "桃園市", 121.203986, 24.952786),
    21: StationMetadata(21, "龍潭", "Longtan", "桃園市", 121.21645772, 24.86400048),
    22: StationMetadata(22, "湖口", "Hukou", "新竹縣", 121.03886894, 24.90009696),
    23: StationMetadata(23, "竹東", "Zhudong", "新竹縣", 121.08895493, 24.74091408),
    24: StationMetadata(24, "新竹", "Hsinchu", "新竹市", 120.97236752, 24.8056356),
    25: StationMetadata(25, "頭份", "Toufen", "苗栗縣", 120.89869286, 24.69690679),
    26: StationMetadata(26, "苗栗", "Miaoli", "苗栗縣", 120.82011468, 24.56499183),
    27: StationMetadata(27, "三義", "Sanyi", "苗栗縣", 120.75956754, 24.38248443),
    28: StationMetadata(28, "豐原", "Fengyuan", "臺中市", 120.74252414, 24.25699731),
    29: StationMetadata(29, "沙鹿", "Shalu", "臺中市", 120.568794, 24.225628),
    30: StationMetadata(30, "大里", "Dali", "臺中市", 120.67844444, 24.09961111),
    31: StationMetadata(31, "忠明", "Zhongming", "臺中市", 120.641092, 24.151958),
    32: StationMetadata(32, "西屯", "Xitun", "臺中市", 120.616917, 24.162197),
    33: StationMetadata(33, "彰化", "Changhua", "彰化縣", 120.541519, 24.066),
    34: StationMetadata(34, "線西", "Xianxi", "彰化縣", 120.469061, 24.131672),
    35: StationMetadata(35, "二林", "Erlin", "彰化縣", 120.409653, 23.925175),
    36: StationMetadata(36, "南投", "Nantou", "南投縣", 120.685306, 23.913),
    37: StationMetadata(37, "斗六", "Douliu", "雲林縣", 120.544994, 23.711853),
    38: StationMetadata(38, "崙背", "Lunbei", "雲林縣", 120.348742, 23.757547),
    39: StationMetadata(39, "新港", "Xingang", "嘉義縣", 120.345531, 23.554839),
    40: StationMetadata(40, "朴子", "Puzi", "嘉義縣", 120.2478, 23.46538),
    41: StationMetadata(41, "臺西", "Taixi", "雲林縣", 120.19933333, 23.702175),
    42: StationMetadata(42, "嘉義", "Chiayi", "嘉義市", 120.44125148, 23.46477865),
    43: StationMetadata(43, "新營", "Xinying", "臺南市", 120.31725, 23.305633),
    44: StationMetadata(44, "善化", "Shanhua", "臺南市", 120.29740529, 23.11337642),
    45: StationMetadata(45, "安南", "Annan", "臺南市", 120.2175, 23.048197),
    46: StationMetadata(46, "臺南", "Tainan", "臺南市", 120.21947897, 22.98928311),
    47: StationMetadata(47, "美濃", "Meinong", "高雄市", 120.530542, 22.883583),
    48: StationMetadata(48, "橋頭", "Qiaotou", "高雄市", 120.305689, 22.757506),
    49: StationMetadata(49, "仁武", "Renwu", "高雄市", 120.332631, 22.689056),
    50: StationMetadata(50, "鳳山", "Fengshan", "高雄市", 120.357422, 22.628126),
    51: StationMetadata(51, "大寮", "Daliao", "高雄市", 120.425311, 22.56413611),
    52: StationMetadata(52, "林園", "Linyuan", "高雄市", 120.41175, 22.4795),
    53: StationMetadata(53, "楠梓", "Nanzi", "高雄市", 120.328289, 22.733667),
    54: StationMetadata(54, "左營", "Zuoying", "高雄市", 120.292917, 22.674861),
    56: StationMetadata(56, "前金", "Qianjin", "高雄市", 120.28676111, 22.63390278),
    57: StationMetadata(57, "前鎮", "Qianzhen", "高雄市", 120.30833356, 22.6044507),
    58: StationMetadata(58, "小港", "Xiaogang", "高雄市", 120.337736, 22.565833),
    59: StationMetadata(59, "屏東", "Pingtung", "屏東縣", 120.488033, 22.673081),
    60: StationMetadata(60, "潮州", "Chaozhou", "屏東縣", 120.561175, 22.523108),
    61: StationMetadata(61, "恆春", "Hengchun", "屏東縣", 120.788928, 21.958069),
    62: StationMetadata(62, "臺東", "Taitung", "臺東縣", 121.15045, 22.755358),
    63: StationMetadata(63, "花蓮", "Hualien", "花蓮縣", 121.599769, 23.971306),
    64: StationMetadata(64, "陽明", "Yangming", "臺北市", 121.529583, 25.182722),
    65: StationMetadata(65, "宜蘭", "Yilan", "宜蘭縣", 121.746394, 24.747917),
    66: StationMetadata(66, "冬山", "Dongshan", "宜蘭縣", 121.792928, 24.632203),
    67: StationMetadata(67, "三重", "Sanchong", "新北市", 121.493806, 25.072611),
    68: StationMetadata(68, "中壢", "Zhongli", "桃園市", 121.221667, 24.953278),
    69: StationMetadata(69, "竹山", "Zhushan", "南投縣", 120.677306, 23.756389),
    70: StationMetadata(70, "永和", "Yonghe", "新北市", 121.516306, 25.017),
    71: StationMetadata(71, "復興", "Fuxing", "高雄市", 120.312017, 22.608711),
    72: StationMetadata(72, "埔里", "Puli", "南投縣", 120.967903, 23.968842),
    75: StationMetadata(75, "馬祖", "Matsu", "連江縣", 119.952724, 26.153736),
    77: StationMetadata(77, "金門", "Kinmen", "金門縣", 118.312256, 24.432133),
    78: StationMetadata(78, "馬公", "Magong", "澎湖縣", 119.566158, 23.569031),
    80: StationMetadata(80, "關山", "Guanshan", "臺東縣", 121.161933, 23.045083),
    83: StationMetadata(83, "麥寮", "Mailiao", "雲林縣", 120.251825, 23.753506),
    84: StationMetadata(84, "富貴角", "FugueiCape", "新北市", 121.53656894, 25.29681695),
    85: StationMetadata(85, "大城", "Dacheng", "彰化縣", 120.26964167, 23.85493056),
    88: StationMetadata(88, "臺灣大道", "Taiwan Avenue", "臺中市", 120.6567111, 24.1589),
    139: StationMetadata(139, "員林", "Yuanlin", "彰化縣", 120.5631893, 23.9615945),
    140: StationMetadata(140, "林森", "Linsen", "臺南市", 120.22216042, 22.98522502),
    201: StationMetadata(201, "宜蘭（三星）", "", "宜蘭縣", 121.6565272, 24.6757916),
    202: StationMetadata(202, "高雄（湖內）", "", "高雄市", 120.24535, 22.87985556),
    203: StationMetadata(203, "南投（鹿谷）", "Nantou（Lugu）", "南投縣", 120.7944772, 23.71867609),
    204: StationMetadata(204, "屏東（琉球）", "Pingtung（Liuqiu）", "屏東縣", 120.37722, 22.35222),
    311: StationMetadata(311, "新北（樹林）", "New Taipei（Shulin）", "新北市", 121.38352778, 24.94902778),
    312: StationMetadata(312, "臺南（南化）", "", "臺南市", 120.44583156, 23.04562013),
    313: StationMetadata(313, "屏東（枋山）", "Pingtung（fangshan）", "屏東縣", 120.651472, 22.260899),
    314: StationMetadata(314, "嘉義（建國路）", "Chiayi（Performing Arts Center）", "嘉義縣", 120.432686, 23.54511),
}

def get_station_by_id(site_id: int) -> Optional[StationMetadata]:
    """Retrieve station metadata by SiteId."""
    return TAIWAN_AQI_STATIONS.get(site_id)

def get_all_stations() -> List[StationMetadata]:
    """Return all known station metadata objects."""
    return list(TAIWAN_AQI_STATIONS.values())
