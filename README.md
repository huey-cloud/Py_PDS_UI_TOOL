# 설비 알람 현황 모니터 (Equipment Alarm Monitor)

삼성전자/SK하이닉스 등 반도체 Fab 설비의 알람·에러 이력을
지도에서 공장을 선택해 CSV/Excel로 불러와 확인하고 시각화하는 데스크톱 GUI 툴.

## 화면 흐름
1. 앱 실행 → **실제 지도 화면** (OpenStreetMap 타일, Leaflet.js, 경기/충청 권역으로 기본 줌인)
2. 지도 위 공장 마커 클릭 → 팝업에서 "상세 보기" 클릭 → 해당 공장의 알람 대시보드로 이동
3. 대시보드에서 라인/심각도 필터, 테이블/차트 확인, 필요시 다른 CSV/Excel로 교체
4. "← 지도로" 버튼으로 지도 화면 복귀

> **인터넷 연결이 필요합니다** (OpenStreetMap 타일을 실시간으로 받아옴). API 키는 필요 없습니다.
> 사내망처럼 인터넷이 안 되는 환경에서는 `src/ui/widgets/map_view.py` (오프라인 SVG 개략도 버전)로
> `main_window.py`의 `LeafletMapView` 부분만 `MapView`로 바꿔서 쓸 수 있습니다.

## 기술 스택
- Python 3.12
- PySide6 (GUI) + **PySide6 QtWebEngine** (Leaflet.js 지도를 웹뷰로 임베드)
- Leaflet.js + OpenStreetMap 타일 (CDN, 무료, API 키 불필요)
- pandas / openpyxl (데이터 처리)
- matplotlib (차트 시각화)

## 실행 방법

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

python -m src.main
```

지도에서 공장을 클릭하면 `sample_data/sites/` 아래 있는 샘플 CSV가 자동으로 로드됩니다.

## 데이터 포맷

CSV/Excel 파일은 다음 컬럼(한글 헤더)을 포함해야 합니다:

| 설비ID | 설비명 | 라인 | 알람코드 | 알람명 | 발생일시 | 해제일시 | 심각도 |
|---|---|---|---|---|---|---|---|

- 심각도는 `Critical` / `Major` / `Minor` 중 하나
- 헤더 이름과 매핑은 `src/data/models.py`의 `COLUMN_ALIASES`에서 관리하므로
  실제 사내 파일의 헤더가 다르면 여기에 추가하면 됩니다.

## 공장(사이트) 추가/수정하기

`src/data/sites.py`의 `SITES` 리스트에 항목을 추가하면 지도에 자동으로 마커가 생깁니다.

```python
Site("사이트ID", "표시이름", "회사명", 위도, 경도, "sample_data/sites/ 아래 csv 파일명"),
```

- 위경도는 실제 값을 입력하면 지도에 정확한 위치로 표시됨
- 해당 `sample_csv` 파일이 없으면 대시보드에서 "다른 파일 열기"로 직접 선택 가능
- 지도 초기 중심/확대 레벨은 `src/ui/widgets/leaflet_map_view.py`의
  `_INITIAL_CENTER`, `_INITIAL_ZOOM` 값을 바꾸면 됨

## 프로젝트 구조

```
assets/
└── korea_map.svg        # (오프라인 대체용) 간략화된 지도 개략도
src/
├── main.py               # 앱 진입점
├── data/
│   ├── loader.py         # CSV/Excel 로딩 & 검증
│   ├── models.py         # 표준 컬럼 스키마
│   ├── sites.py           # 공장(사이트) 목록
│   └── geo_projection.py # (오프라인 SVG용) 위경도->픽셀 좌표 투영
└── ui/
    ├── main_window.py     # 지도<->대시보드 화면 전환
    ├── dashboard_widget.py# 공장별 알람 대시보드 (테이블+차트+필터)
    └── widgets/
        ├── leaflet_map_view.py # 실제 지도 위젯 (OSM + Leaflet, 기본 사용)
        ├── map_view.py          # (오프라인 대체용) SVG 개략도 지도 위젯
        ├── alarm_table.py       # 알람 이력 테이블
        └── alarm_chart.py       # 설비별/일자별 차트
sample_data/
├── sample_alarms.csv     # 초기 단일 CSV 샘플 (참고용)
└── sites/                # 공장별 샘플 CSV
tools/
└── generate_map.py       # (오프라인 SVG용) 지도 재생성 스크립트
```

## 테스트

```bash
pip install pytest
pytest
```

## 로드맵
- [x] 프로젝트 뼈대 + CSV/Excel 로더
- [x] 기본 GUI (테이블 + 차트 + 필터)
- [x] 지도 화면 + 공장별 대시보드 드릴다운
- [x] 실제 지도(OpenStreetMap/Leaflet)로 전환, 경기/충청 줌인
- [ ] 기간(날짜) 필터 추가
- [ ] 설비별 상세 화면 (드릴다운)
- [ ] 마커에 알람 건수/심각도 뱃지 실시간 표시
- [ ] PyInstaller 패키징

