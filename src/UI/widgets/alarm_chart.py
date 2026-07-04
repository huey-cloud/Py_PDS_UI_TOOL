"""matplotlib 차트를 Qt 위젯에 임베드하여 알람 통계를 시각화."""
from __future__ import annotations

import pandas as pd
from matplotlib import font_manager, rcParams
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

from src.data.models import COL_EQUIPMENT_NAME, COL_OCCURRED_AT, COL_SEVERITY

_SEVERITY_COLOR = {
    "Critical": "#d9534f",
    "Major": "#f0ad4e",
    "Minor": "#5cb85c",
}

# 설치된 한글 폰트를 자동으로 찾아 matplotlib 기본 폰트로 설정한다.
# (Windows: 맑은 고딕, macOS: Apple SD Gothic Neo, Linux: Nanum* 등)
_KOREAN_FONT_CANDIDATES = [
    "Malgun Gothic",
    "AppleGothic",
    "Apple SD Gothic Neo",
    "NanumGothic",
    "Noto Sans CJK KR",
    "Noto Sans KR",
]


def _apply_korean_font() -> None:
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in _KOREAN_FONT_CANDIDATES:
        if name in available:
            rcParams["font.family"] = name
            break
    rcParams["axes.unicode_minus"] = False


_apply_korean_font()


class AlarmChart(QWidget):
    """설비별 알람 건수(막대) + 일자별 추이(선) 두 개의 서브플롯을 보여준다."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(6, 4), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def set_data(self, df: pd.DataFrame) -> None:
        self.figure.clear()
        if df.empty:
            self.canvas.draw()
            return

        ax1 = self.figure.add_subplot(211)
        ax2 = self.figure.add_subplot(212)
        self._plot_by_equipment(ax1, df)
        self._plot_trend(ax2, df)
        self.canvas.draw()

    def _plot_by_equipment(self, ax, df: pd.DataFrame) -> None:
        top = (
            df.groupby(COL_EQUIPMENT_NAME)
            .size()
            .sort_values(ascending=False)
            .head(10)
        )
        ax.bar(top.index.astype(str), top.values, color="#4a90d9")
        ax.set_title("설비별 알람 발생 건수 (상위 10)")
        ax.tick_params(axis="x", rotation=45, labelsize=8)

    def _plot_trend(self, ax, df: pd.DataFrame) -> None:
        daily = df.copy()
        daily["date"] = daily[COL_OCCURRED_AT].dt.date
        pivot = daily.groupby(["date", COL_SEVERITY]).size().unstack(fill_value=0)
        for severity, color in _SEVERITY_COLOR.items():
            if severity in pivot.columns:
                ax.plot(pivot.index, pivot[severity], label=severity, color=color, marker="o")
        ax.set_title("일자별 알람 발생 추이 (심각도별)")
        ax.legend(fontsize=8)
        ax.tick_params(axis="x", rotation=45, labelsize=8)
