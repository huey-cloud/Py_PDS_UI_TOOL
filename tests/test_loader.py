from pathlib import Path

import pytest

from src.data.loader import LoadError, load_alarm_file, summarize

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "sample_data" / "sample_alarms.csv"


def test_load_sample_csv():
    df = load_alarm_file(SAMPLE_PATH)
    assert len(df) == 10
    assert set(df["severity"].unique()) <= {"Critical", "Major", "Minor"}


def test_summarize_counts():
    df = load_alarm_file(SAMPLE_PATH)
    summary = summarize(df)
    assert summary.total_count == 10
    assert summary.critical_count + summary.major_count + summary.minor_count == 10
    assert summary.equipment_count == 5


def test_missing_file_raises():
    with pytest.raises(LoadError):
        load_alarm_file("no_such_file.csv")
