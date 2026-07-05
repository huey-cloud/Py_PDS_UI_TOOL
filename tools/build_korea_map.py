"""
southkorea/southkorea-maps 저장소의 시도 경계 GeoJSON을 병합/단순화해서
assets/korea_map.svg 를 다시 생성하는 1회성 스크립트.

이 스크립트 자체는 배포 대상이 아니고, 지도 품질을 개선할 때 다시 실행하기 위해
프로젝트 루트의 tools/ 에 보관한다.
"""
import json
import math
from pathlib import Path

from shapely.geometry import shape
from shapely.ops import unary_union

SOURCE_GEOJSON = Path(__file__).resolve().parent / "korea_provinces_source.json"
OUTPUT_SVG = Path(__file__).resolve().parents[1] / "assets" / "korea_map.svg"

# 표시할 섬 개수 (면적 상위 N개 + 울릉도는 강제 포함)
TOP_N_ISLANDS = 9
SIMPLIFY_TOLERANCE = 0.004  # 단위: 度. 값이 클수록 해안선이 매끈해지는 대신 디테일이 줄어듦

# 지도 좌표계 스케일 (px / 度). sites.py 와 반드시 동일해야 마커 위치가 맞는다.
PX_PER_DEGREE = 100.0
PADDING_DEGREE = 0.15  # 지도 가장자리 여백


def load_merged_geometry():
    data = json.loads(SOURCE_GEOJSON.read_text(encoding="utf-8"))
    geoms = [shape(f["geometry"]) for f in data["features"]]
    return unary_union(geoms)


def pick_visible_polygons(merged):
    polys = list(merged.geoms)
    by_area = sorted(polys, key=lambda p: p.area, reverse=True)
    chosen = by_area[:TOP_N_ISLANDS]
    # 울릉도(동쪽 끝 섬)는 크기는 작지만 상징성이 있어 강제로 포함
    ulleung = [p for p in polys if p.bounds[2] > 130.5]
    for p in ulleung:
        if p not in chosen:
            chosen.append(p)
    return chosen


def make_projector(lon_min, lat_min, lon_max, lat_max):
    lon_min -= PADDING_DEGREE
    lon_max += PADDING_DEGREE
    lat_min -= PADDING_DEGREE
    lat_max += PADDING_DEGREE
    mean_lat = (lat_min + lat_max) / 2
    cos_lat = math.cos(math.radians(mean_lat))

    def project(lon, lat):
        x = (lon - lon_min) * cos_lat * PX_PER_DEGREE
        y = (lat_max - lat) * PX_PER_DEGREE
        return x, y

    width = (lon_max - lon_min) * cos_lat * PX_PER_DEGREE
    height = (lat_max - lat_min) * PX_PER_DEGREE
    return project, width, height, (lon_min, lon_max, lat_min, lat_max)


def polygon_to_path(polygon, project) -> str:
    def ring_to_d(coords):
        pts = [project(lon, lat) for lon, lat in coords]
        d = f"M {pts[0][0]:.2f},{pts[0][1]:.2f} "
        d += " ".join(f"L {x:.2f},{y:.2f}" for x, y in pts[1:])
        d += " Z"
        return d

    parts = [ring_to_d(list(polygon.exterior.coords))]
    for interior in polygon.interiors:
        parts.append(ring_to_d(list(interior.coords)))
    return " ".join(parts)


def main():
    merged = load_merged_geometry()
    minx, miny, maxx, maxy = merged.bounds  # 전체(작은 섬 포함) 기준으로 스케일 산정
    project, width, height, bounds = make_projector(minx, miny, maxx, maxy)

    visible = pick_visible_polygons(merged)
    simplified = [p.simplify(SIMPLIFY_TOLERANCE, preserve_topology=True) for p in visible]

    path_elements = []
    for p in simplified:
        d = polygon_to_path(p, project)
        path_elements.append(f'  <path d="{d}" />')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}">
  <!--
    남한 해안선 개략도.
    출처: southkorea/southkorea-maps (KOSTAT 2013 시도 경계, GeoJSON) 를
    병합(unary_union) + 단순화(simplify tolerance={SIMPLIFY_TOLERANCE}) 해서 생성.
    실제 좌표 기반이지만 작은 섬 다수는 시인성을 위해 생략했다.
    이 파일은 tools/build_korea_map.py 로 재생성할 수 있다.
  -->
  <defs>
    <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#eef5fb"/>
      <stop offset="100%" stop-color="#dbe9f5"/>
    </linearGradient>
    <linearGradient id="land" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#e7efe0"/>
      <stop offset="100%" stop-color="#d3e0c8"/>
    </linearGradient>
    <filter id="landShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1.5" stdDeviation="2" flood-color="#5b6b52" flood-opacity="0.25"/>
    </filter>
  </defs>

  <rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" fill="url(#sea)"/>

  <g fill="url(#land)" stroke="#8fa480" stroke-width="1.6" stroke-linejoin="round" filter="url(#landShadow)">
{chr(10).join(path_elements)}
  </g>
</svg>
'''
    OUTPUT_SVG.write_text(svg, encoding="utf-8")
    print(f"저장됨: {OUTPUT_SVG}")
    print(f"viewBox: 0 0 {width:.1f} {height:.1f}")
    print(f"경도 범위(패딩 포함): {bounds[0]:.4f} ~ {bounds[1]:.4f}")
    print(f"위도 범위(패딩 포함): {bounds[2]:.4f} ~ {bounds[3]:.4f}")
    print(f"표시된 섬(폴리곤) 수: {len(simplified)}")


if __name__ == "__main__":
    main()
