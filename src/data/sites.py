"""전국 공장(사이트) 목록과 위경도 -> 지도 좌표 변환.

지도 좌표 변환은 src/data/geo_projection.py 에 있는 투영 로직을 그대로 쓴다.
(assets/korea_map.svg 를 만드는 tools/generate_map.py 와 동일한 투영을 공유)
"""
from __future__ import annotations

from dataclasses import dataclass

from src.data.geo_projection import lonlat_to_xy


@dataclass(frozen=True)
class Site:
    site_id: str
    name: str
    company: str
    lat: float
    lon: float
    sample_csv: str  # sample_data/sites/ 아래 파일명

    def map_xy(self) -> tuple[float, float]:
        """지도 SVG 좌표계 기준 (x, y) 픽셀 위치를 계산."""
        return lonlat_to_xy(self.lon, self.lat)


SITES: list[Site] = [
    Site("samsung_pyeongtaek", "삼성전자 평택캠퍼스", "삼성전자", 37.0396, 127.0092, "samsung_pyeongtaek.csv"),
    Site("samsung_giheung", "삼성전자 기흥캠퍼스", "삼성전자", 37.2749, 127.1136, "samsung_giheung.csv"),
    Site("samsung_hwaseong", "삼성전자 화성캠퍼스", "삼성전자", 37.2038, 126.8398, "samsung_hwaseong.csv"),
    Site("skhynix_icheon", "SK하이닉스 이천캠퍼스", "SK하이닉스", 37.2636, 127.4423, "skhynix_icheon.csv"),
    Site("skhynix_cheongju", "SK하이닉스 청주캠퍼스", "SK하이닉스", 36.6357, 127.4917, "skhynix_cheongju.csv"),
]

SITE_BY_ID: dict[str, Site] = {s.site_id: s for s in SITES}

COMPANY_COLOR = {
    "삼성전자": "#1428a0",
    "SK하이닉스": "#e60012",
}
