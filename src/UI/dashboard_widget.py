"""선택된 공장(사이트)의 알람 이력을 보여주는 대시보드 위젯."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.data.loader import LoadError, load_alarm_file, summarize
from src.data.models import COL_LINE, COL_SEVERITY, SEVERITY_ORDER
from src.data.sites import Site
from src.ui.widgets.alarm_chart import AlarmChart
from src.ui.widgets.alarm_table import AlarmTable

_SAMPLE_DIR = Path(__file__).resolve().parents[2] / "sample_data" / "sites"


class DashboardWidget(QWidget):
    """지도에서 선택된 공장 하나에 대한 알람 현황 화면."""

    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._raw_df: pd.DataFrame = pd.DataFrame()
        self._current_site: Site | None = None
        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.addLayout(self._build_toolbar())

        self._summary_label = QLabel("공장을 선택하면 알람 이력을 불러옵니다.")
        root_layout.addWidget(self._summary_label)

        splitter = QSplitter()
        self._table = AlarmTable()
        self._chart = AlarmChart()
        splitter.addWidget(self._table)
        splitter.addWidget(self._chart)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        root_layout.addWidget(splitter, stretch=1)

    def _build_toolbar(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        back_btn = QPushButton("← 지도로")
        back_btn.clicked.connect(self.back_requested.emit)
        layout.addWidget(back_btn)

        self._title_label = QLabel("")
        self._title_label.setStyleSheet("font-weight: bold; font-size: 15px; margin-left: 8px;")
        layout.addWidget(self._title_label)

        layout.addStretch(1)

        open_btn = QPushButton("다른 파일 열기 (CSV/Excel)")
        open_btn.clicked.connect(self._on_open_file)
        layout.addWidget(open_btn)

        layout.addWidget(QLabel("라인:"))
        self._line_filter = QComboBox()
        self._line_filter.addItem("전체")
        self._line_filter.currentIndexChanged.connect(self._apply_filters)
        layout.addWidget(self._line_filter)

        layout.addWidget(QLabel("심각도:"))
        self._severity_filter = QComboBox()
        self._severity_filter.addItem("전체")
        self._severity_filter.addItems(SEVERITY_ORDER)
        self._severity_filter.currentIndexChanged.connect(self._apply_filters)
        layout.addWidget(self._severity_filter)

        return layout

    # -------------------------------------------------------- 공개 인터페이스
    def load_site(self, site: Site) -> None:
        """지도에서 사이트를 선택했을 때 호출. 샘플 CSV가 있으면 자동으로 불러온다."""
        self._current_site = site
        self._title_label.setText(f"{site.name} ({site.company})")

        sample_path = _SAMPLE_DIR / site.sample_csv
        if sample_path.exists():
            self._load_path(sample_path)
        else:
            self._raw_df = pd.DataFrame()
            self._summary_label.setText(
                "해당 공장의 샘플 데이터가 없습니다. '다른 파일 열기'로 CSV/Excel을 불러오세요."
            )
            self._table.set_data(self._raw_df)
            self._chart.set_data(self._raw_df)

    # ------------------------------------------------------------- actions
    def _on_open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "알람 이력 파일 선택",
            "",
            "지원 파일 (*.csv *.xlsx *.xls);;CSV (*.csv);;Excel (*.xlsx *.xls)",
        )
        if not path:
            return
        self._load_path(Path(path))

    def _load_path(self, path: Path) -> None:
        try:
            df = load_alarm_file(path)
        except LoadError as exc:
            QMessageBox.critical(self, "파일 로딩 실패", str(exc))
            return

        self._raw_df = df
        self._refresh_line_filter()
        self._apply_filters()

    def _refresh_line_filter(self) -> None:
        self._line_filter.blockSignals(True)
        self._line_filter.clear()
        self._line_filter.addItem("전체")
        if not self._raw_df.empty:
            lines = sorted(self._raw_df[COL_LINE].dropna().astype(str).unique())
            self._line_filter.addItems(lines)
        self._line_filter.blockSignals(False)

    def _apply_filters(self) -> None:
        df = self._raw_df
        if df.empty:
            self._table.set_data(df)
            self._chart.set_data(df)
            return

        line = self._line_filter.currentText()
        if line and line != "전체":
            df = df[df[COL_LINE].astype(str) == line]

        severity = self._severity_filter.currentText()
        if severity and severity != "전체":
            df = df[df[COL_SEVERITY] == severity]

        self._table.set_data(df)
        self._chart.set_data(df)
        self._update_summary(df)

    def _update_summary(self, df: pd.DataFrame) -> None:
        summary = summarize(df)
        if summary.total_count == 0:
            self._summary_label.setText("표시할 알람 이력이 없습니다.")
            return

        start, end = summary.date_range
        period = ""
        if start is not None and end is not None:
            period = f" | 기간: {start:%Y-%m-%d} ~ {end:%Y-%m-%d}"

        self._summary_label.setText(
            f"총 {summary.total_count}건  "
            f"(Critical {summary.critical_count} / Major {summary.major_count} / Minor {summary.minor_count})  "
            f"| 설비 수: {summary.equipment_count}{period}"
        )
