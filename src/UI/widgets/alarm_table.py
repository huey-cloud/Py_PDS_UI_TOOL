"""알람 이력을 보여주는 테이블 위젯."""
from __future__ import annotations

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

from src.data.models import (
    COL_ALARM_CODE,
    COL_ALARM_NAME,
    COL_CLEARED_AT,
    COL_EQUIPMENT_ID,
    COL_EQUIPMENT_NAME,
    COL_LINE,
    COL_OCCURRED_AT,
    COL_SEVERITY,
)

_DISPLAY_COLUMNS = [
    (COL_EQUIPMENT_ID, "설비ID"),
    (COL_EQUIPMENT_NAME, "설비명"),
    (COL_LINE, "라인"),
    (COL_ALARM_CODE, "알람코드"),
    (COL_ALARM_NAME, "알람명"),
    (COL_SEVERITY, "심각도"),
    (COL_OCCURRED_AT, "발생일시"),
    (COL_CLEARED_AT, "해제일시"),
]

_SEVERITY_COLOR = {
    "Critical": "#ffb3b3",
    "Major": "#ffe0a3",
    "Minor": "#d9f2d9",
}


class AlarmTable(QTableWidget):
    """pandas DataFrame을 그대로 표시하는 읽기 전용 테이블."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(_DISPLAY_COLUMNS))
        self.setHorizontalHeaderLabels([label for _, label in _DISPLAY_COLUMNS])
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
        self.horizontalHeader().setStretchLastSection(True)

    def set_data(self, df: pd.DataFrame) -> None:
        self.setSortingEnabled(False)
        self.setRowCount(len(df))
        for row_idx, (_, row) in enumerate(df.iterrows()):
            severity = str(row.get(COL_SEVERITY, ""))
            for col_idx, (col_key, _) in enumerate(_DISPLAY_COLUMNS):
                value = row.get(col_key, "")
                if pd.isna(value):
                    text = ""
                elif hasattr(value, "strftime"):
                    text = value.strftime("%Y-%m-%d %H:%M")
                else:
                    text = str(value)
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                color = _SEVERITY_COLOR.get(severity)
                if color:
                    item.setBackground(QColor(color))
                self.setItem(row_idx, col_idx, item)
        self.setSortingEnabled(True)
        self.resizeColumnsToContents()
