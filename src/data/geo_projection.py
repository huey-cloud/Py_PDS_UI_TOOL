"""위경도 -> 지도(SVG) 픽셀 좌표 변환 로직.

assets/korea_map.svg 를 만드는 tools/generate_map.py 와
지도 위 마커 위치를 계산하는 src/data/sites.py 가 반드시 같은 투영을
사용해야 해안선과 마커 위치가 어긋나지 않는다. 그래서 이 로직을
한 곳에 모아두고 양쪽에서 가져다 쓴다.
"""
from __future__ import annotations

import math
from functools import lru_cache

REF_LAT = 36.5  # 경도 왜곡 보정 기준 위도
CANVAS_WIDTH = 480.0
CANVAS_MARGIN = 24.0

# 남한 본토 국경 (간략화), 출처: johan/world.geo.json countries/KOR.geo.json (MIT License)
MAINLAND_COORDS: list[tuple[float, float]] = [
    (128.349716, 38.612243), (129.21292, 37.432392), (129.46045, 36.784189),
    (129.468304, 35.632141), (129.091377, 35.082484), (128.18585, 34.890377),
    (127.386519, 34.475674), (126.485748, 34.390046), (126.37392, 34.93456),
    (126.559231, 35.684541), (126.117398, 36.725485), (126.860143, 36.893924),
    (126.174759, 37.749686), (126.237339, 37.840378), (126.68372, 37.804773),
    (127.073309, 38.256115), (127.780035, 38.304536), (128.205746, 38.370397),
    (128.349716, 38.612243),
]

# 제주도는 위 데이터셋에 없어 대략적인 타원으로 별도 표시 (중심 좌표만 근사치)
JEJU_CENTER = (126.53, 33.38)
JEJU_RADIUS_DEG = (0.42, 0.22)


def _jeju_ellipse_points(steps: int = 24) -> list[tuple[float, float]]:
    cx, cy = JEJU_CENTER
    rx, ry = JEJU_RADIUS_DEG
    return [
        (cx + rx * math.cos(2 * math.pi * i / steps), cy + ry * math.sin(2 * math.pi * i / steps))
        for i in range(steps)
    ]


@lru_cache(maxsize=1)
def _bounds() -> tuple[float, float, float, float, float, float]:
    """(px_min, px_max, py_min, py_max, scale, canvas_height)"""
    all_lonlat = list(MAINLAND_COORDS) + _jeju_ellipse_points()
    ref_rad = math.radians(REF_LAT)
    proj = [(lon * math.cos(ref_rad), lat) for lon, lat in all_lonlat]

    px_min = min(p[0] for p in proj)
    px_max = max(p[0] for p in proj)
    py_min = min(p[1] for p in proj)
    py_max = max(p[1] for p in proj)

    usable_w = CANVAS_WIDTH - 2 * CANVAS_MARGIN
    scale = usable_w / (px_max - px_min)
    canvas_height = (py_max - py_min) * scale + 2 * CANVAS_MARGIN
    return px_min, px_max, py_min, py_max, scale, canvas_height


def canvas_size() -> tuple[float, float]:
    *_ignore, scale, canvas_height = _bounds()
    return CANVAS_WIDTH, canvas_height


def lonlat_to_xy(lon: float, lat: float) -> tuple[float, float]:
    """cos(위도) 보정을 적용한 등거리원통 투영으로 (경도, 위도) -> 픽셀 좌표 변환."""
    px_min, _px_max, _py_min, py_max, scale, _canvas_height = _bounds()
    ref_rad = math.radians(REF_LAT)
    px = lon * math.cos(ref_rad)
    py = lat
    x = CANVAS_MARGIN + (px - px_min) * scale
    y = CANVAS_MARGIN + (py_max - py) * scale
    return x, y


def jeju_ellipse_xy(steps: int = 24) -> list[tuple[float, float]]:
    return [lonlat_to_xy(lon, lat) for lon, lat in _jeju_ellipse_points(steps)]


def mainland_xy() -> list[tuple[float, float]]:
    return [lonlat_to_xy(lon, lat) for lon, lat in MAINLAND_COORDS]
