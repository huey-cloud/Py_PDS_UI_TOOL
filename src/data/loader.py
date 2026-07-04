"""
CSV / Excel 파일에서 설비 알람 이력을 읽어와
표준 스키마(models.py)로 정규화하는 로더.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .models import (
    COLUMN_ALIASES,
    COL_CLEARED_AT,
    COL_OCCURRED_AT,
    COL_SEVERITY,
    REQUIRED_COLUMNS,
    AlarmSummary,
)


class LoadError(Exception):
    """파일 로딩/검증 실패 시 발생하는 예외. UI에서 메시지박스로 그대로 보여준다."""


def load_alarm_file(path: str | Path) -> pd.DataFrame:
    """CSV 또는 Excel 파일을 읽어 표준 컬럼명을 가진 DataFrame으로 반환한다.

    Raises:
        LoadError: 확장자를 지원하지 않거나 필수 컬럼이 없을 때
    """
    path = Path(path)
    if not path.exists():
        raise LoadError(f"파일을 찾을 수 없습니다: {path}")

    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            df = pd.read_csv(path, encoding="utf-8-sig")
        elif suffix in (".xlsx", ".xls"):
            df = pd.read_excel(path)
        else:
            raise LoadError(f"지원하지 않는 파일 형식입니다: {suffix} (csv, xlsx만 지원)")
    except LoadError:
        raise
    except Exception as exc:  # pandas 파싱 에러 등
        raise LoadError(f"파일을 읽는 중 오류가 발생했습니다: {exc}") from exc

    df = _normalize_columns(df)
    _validate_columns(df)
    df = _coerce_types(df)
    return df


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """원본 헤더(한글/영문 등)를 표준 컬럼명으로 매핑한다."""
    rename_map = {}
    for col in df.columns:
        key = str(col).strip()
        if key in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[key]
    return df.rename(columns=rename_map)


def _validate_columns(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise LoadError(
            "필수 컬럼이 없습니다: "
            + ", ".join(missing)
            + "\n(파일 헤더를 확인하거나 models.py의 COLUMN_ALIASES에 매핑을 추가하세요)"
        )


def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    df[COL_OCCURRED_AT] = pd.to_datetime(df[COL_OCCURRED_AT], errors="coerce")
    df[COL_CLEARED_AT] = pd.to_datetime(df[COL_CLEARED_AT], errors="coerce")
    df[COL_SEVERITY] = df[COL_SEVERITY].astype(str).str.strip().str.capitalize()
    return df


def summarize(df: pd.DataFrame) -> AlarmSummary:
    """대시보드 상단 카드에 쓸 요약 통계 계산."""
    if df.empty:
        return AlarmSummary(0, 0, 0, 0, 0, (None, None))

    severity_counts = df[COL_SEVERITY].value_counts()
    return AlarmSummary(
        total_count=len(df),
        critical_count=int(severity_counts.get("Critical", 0)),
        major_count=int(severity_counts.get("Major", 0)),
        minor_count=int(severity_counts.get("Minor", 0)),
        equipment_count=df["equipment_id"].nunique(),
        date_range=(df[COL_OCCURRED_AT].min(), df[COL_OCCURRED_AT].max()),
    )
