"""Leaflet.js + OpenStreetMap 타일을 이용한 실제 지도 위젯.

- API 키 불필요 (OSM 무료 타일), 인터넷 연결 필요.
- 마커 클릭은 Leaflet 안에서 커스텀 URL 스킴(site://<site_id>)으로 이동시키고,
  QWebEnginePage.acceptNavigationRequest 에서 그 이동을 가로채 시그널로 변환한다.
  (QWebChannel 없이 가볍게 클릭 이벤트만 파이썬으로 전달하는 방식)
"""
from __future__ import annotations

import json

from PySide6.QtCore import QUrl, Signal
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView

from src.data.sites import COMPANY_COLOR, SITES

# 경기/충청 권역을 기본으로 보여주기 위한 초기 중심/줌
_INITIAL_CENTER = (36.95, 127.15)
_INITIAL_ZOOM = 9


class _BridgePage(QWebEnginePage):
    """지도 안에서 'site://<site_id>' 로의 가짜 이동을 가로채 콜백으로 넘긴다."""

    def __init__(self, on_site_click, parent=None):
        super().__init__(parent)
        self._on_site_click = on_site_click

    def acceptNavigationRequest(self, url: QUrl, nav_type, is_main_frame) -> bool:  # noqa: N802
        if url.scheme() == "site":
            self._on_site_click(url.host())
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


def _build_html() -> str:
    markers = [
        {
            "id": s.site_id,
            "name": s.name,
            "company": s.company,
            "lat": s.lat,
            "lon": s.lon,
            "color": COMPANY_COLOR.get(s.company, "#666666"),
        }
        for s in SITES
    ]
    markers_json = json.dumps(markers, ensure_ascii=False)
    center_lat, center_lon = _INITIAL_CENTER

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
  html, body, #map {{ height: 100%; margin: 0; padding: 0; background: #dceaf5; }}
  .site-marker {{
    width: 22px; height: 22px; border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    border: 2px solid #ffffff;
    box-shadow: 0 1px 4px rgba(0,0,0,0.4);
  }}
  .site-marker-inner {{
    transform: rotate(45deg);
    width: 100%; height: 100%;
    display: flex; align-items: center; justify-content: center;
  }}
  .leaflet-popup-content {{ font-family: -apple-system, "Malgun Gothic", sans-serif; }}
  .popup-title {{ font-weight: bold; margin-bottom: 4px; }}
  .leaflet-popup-content a.popup-btn {{
    display: inline-block; margin-top: 6px; padding: 4px 10px;
    background: #2563eb; color: #ffffff !important;
    border-radius: 4px; text-decoration: none; font-size: 12px;
  }}
  .leaflet-popup-content a.popup-btn:visited,
  .leaflet-popup-content a.popup-btn:hover {{
    color: #ffffff !important;
  }}
</style>
</head>
<body>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
  const sites = {markers_json};

  const map = L.map('map', {{ zoomControl: true }})
    .setView([{center_lat}, {center_lon}], {_INITIAL_ZOOM});

  L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }}).addTo(map);

  function makeIcon(color) {{
    return L.divIcon({{
      className: '',
      html: `<div class="site-marker" style="background:${{color}}">
               <div class="site-marker-inner"></div>
             </div>`,
      iconSize: [22, 22],
      iconAnchor: [11, 22],
      popupAnchor: [0, -20],
    }});
  }}

  sites.forEach(function (site) {{
    const marker = L.marker([site.lat, site.lon], {{ icon: makeIcon(site.color) }}).addTo(map);
    marker.bindPopup(
      `<div class="popup-title">${{site.name}}</div>` +
      `<div>${{site.company}}</div>` +
      `<a class="popup-btn" href="site://${{site.id}}">상세 보기 &rarr;</a>`
    );
  }});
</script>
</body>
</html>
"""


class LeafletMapView(QWebEngineView):
    """OSM 기반 실제 지도. 마커 클릭(팝업의 '상세 보기') 시 site_selected 시그널 발생."""

    site_selected = Signal(str)  # site_id 전달

    def __init__(self, parent=None):
        super().__init__(parent)
        page = _BridgePage(self._on_site_click, self)
        self.setPage(page)
        self.setHtml(_build_html(), QUrl("https://local.equipment-monitor/"))

    def _on_site_click(self, site_id: str) -> None:
        self.site_selected.emit(site_id)
