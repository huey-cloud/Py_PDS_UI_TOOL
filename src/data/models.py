"""
알람/에러 이력 데이터의 스키마와 상수 정의.

실제 사내 DB/파일 포맷이 정해지면 COLUMN_MAP만 수정해서
내부 표준 컬럼명에 매핑하면 된다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


# 내부적으로 사용할 표준 컬럼명 (이 이름들로 통일해서 이후 로직을 작성한다)
COL_EQUIPMENT_ID = "equipment_id"
COL_EQUIPMENT_NAME = "equipment_name"
COL_LINE = "line"
COL_ALARM_CODE = "alarm_code"
COL_ALARM_NAME = "alarm_name"
COL_OCCURRED_AT = "occurred_at"
COL_CLEARED_AT = "cleared_at"
COL_SEVERITY = "severity"

REQUIRED_COLUMNS = [
    COL_EQUIPMENT_ID,
    COL_EQUIPMENT_NAME,
    COL_LINE,
    COL_ALARM_CODE,
    COL_ALARM_NAME,
    COL_OCCURRED_AT,
    COL_CLEARED_AT,
    COL_SEVERITY,
]

# 사용자 파일의 한글/영문 헤더 -> 내부 표준 컬럼명 매핑
# 여기에 새로운 헤더 이름을 추가하면 다양한 원본 포맷을 그대로 인식할 수 있다.
COLUMN_ALIASES = {
    "설비ID": COL_EQUIPMENT_ID,
    "설비id": COL_EQUIPMENT_ID,
    "equipment_id": COL_EQUIPMENT_ID,
    "설비명": COL_EQUIPMENT_NAME,
    "equipment_name": COL_EQUIPMENT_NAME,
    "라인": COL_LINE,
    "line": COL_LINE,
    "알람코드": COL_ALARM_CODE,
    "alarm_code": COL_ALARM_CODE,
    "알람명": COL_ALARM_NAME,
    "alarm_name": COL_ALARM_NAME,
    "발생일시": COL_OCCURRED_AT,
    "occurred_at": COL_OCCURRED_AT,
    "해제일시": COL_CLEARED_AT,
    "cleared_at": COL_CLEARED_AT,
    "심각도": COL_SEVERITY,
    "severity": COL_SEVERITY,
}

SEVERITY_ORDER = ["Critical", "Major", "Minor"]


@dataclass
class AlarmSummary:
    """로드된 데이터에 대한 요약 통계 (대시보드 상단 카드용)."""

    total_count: int
    critical_count: int
    major_count: int
    minor_count: int
    equipment_count: int
    date_range: tuple[datetime | None, datetime | None]
