"""애플리케이션 메인 윈도우.

화면 흐름:
    지도 화면(LeafletMapView) --[마커 클릭 -> 팝업의 '상세 보기']--> 공장 대시보드(DashboardWidget)
                              <--[← 지도로]--
"""
from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QStackedWidget

from src.data.sites import SITE_BY_ID
from src.ui.dashboard_widget import DashboardWidget
from src.ui.widgets.leaflet_map_view import LeafletMapView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("설비 알람 현황 모니터")
        self.resize(1150, 780)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._map_view = LeafletMapView()
        self._dashboard = DashboardWidget()

        self._stack.addWidget(self._map_view)      # index 0
        self._stack.addWidget(self._dashboard)     # index 1

        self._map_view.site_selected.connect(self._on_site_selected)
        self._dashboard.back_requested.connect(self._show_map)

    def _on_site_selected(self, site_id: str) -> None:
        site = SITE_BY_ID.get(site_id)
        if site is None:
            return
        self._dashboard.load_site(site)
        self._stack.setCurrentIndex(1)

    def _show_map(self) -> None:
        self._stack.setCurrentIndex(0)
