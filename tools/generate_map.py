"""실제 해안선 좌표로 assets/korea_map.svg 를 생성/재생성하는 빌드 스크립트.

좌표/투영 로직은 src/data/geo_projection.py 를 그대로 사용하므로,
지도 위 마커 위치(Site.map_xy)와 해안선이 항상 같은 기준으로 맞는다.

좌표 출처: johan/world.geo.json (MIT License) - 남한 국경 간략화 좌표.
저작권상 문제되는 이미지 자산이 아니라 위경도 좌표(사실 정보)를 바탕으로
직접 SVG를 생성하므로 자유롭게 사용/재생성 가능하다.

사이트를 추가/변경해서 지도를 다시 만들고 싶으면 이 스크립트를 다시 실행:
    python tools/generate_map.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.data.geo_projection import canvas_size, jeju_ellipse_xy, lonlat_to_xy, mainland_xy, JEJU_CENTER, JEJU_RADIUS_DEG


def _catmull_rom_to_bezier_path(points: list[tuple[float, float]], closed: bool = True) -> str:
    """점 목록을 부드러운 곡선(3차 베지어)의 SVG path d 속성으로 변환."""
    n = len(points)
    if n < 3:
        return "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in points)

    def pt(i):
        return points[i % n] if closed else points[max(0, min(n - 1, i))]

    d = [f"M {points[0][0]:.1f},{points[0][1]:.1f}"]
    segment_count = n if closed else n - 1
    for i in range(segment_count):
        p0, p1, p2, p3 = pt(i - 1), pt(i), pt(i + 1), pt(i + 2)
        b1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        b2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C {b1[0]:.1f},{b1[1]:.1f} {b2[0]:.1f},{b2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}")
    d.append("Z")
    return " ".join(d)


def build_svg() -> str:
    width, height = canvas_size()

    mainland_path = _catmull_rom_to_bezier_path(mainland_xy(), closed=True)
    jeju_path = _catmull_rom_to_bezier_path(jeju_ellipse_xy(), closed=True)

    cx, cy = JEJU_CENTER
    _rx, ry = JEJU_RADIUS_DEG
    label_x, label_y = lonlat_to_xy(cx, cy - ry - 0.12)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}">
  <!-- 실제 해안선 좌표(johan/world.geo.json, MIT License) 기반으로 자동 생성된 지도.
       간략화된 좌표를 사용했으므로 정밀 GIS 용도로는 부적합합니다. -->
  <defs>
    <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#eaf4fb"/>
      <stop offset="100%" stop-color="#dceaf5"/>
    </linearGradient>
    <linearGradient id="land" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#e8efe0"/>
      <stop offset="100%" stop-color="#d3e0c6"/>
    </linearGradient>
  </defs>

  <rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" fill="url(#sea)"/>

  <path d="{mainland_path}" fill="url(#land)" stroke="#8fa377" stroke-width="2.2" stroke-linejoin="round"/>
  <path d="{jeju_path}" fill="url(#land)" stroke="#8fa377" stroke-width="2.2" stroke-linejoin="round"/>

  <text x="{label_x:.1f}" y="{label_y:.1f}" font-size="13" fill="#6b7a5c" text-anchor="middle" font-family="sans-serif">제주</text>
</svg>
"""


def main() -> None:
    out_path = _PROJECT_ROOT / "assets" / "korea_map.svg"
    out_path.write_text(build_svg(), encoding="utf-8")
    print(f"지도 생성 완료: {out_path}")


if __name__ == "__main__":
    main()
