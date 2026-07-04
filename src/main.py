"""애플리케이션 진입점.

실행 (둘 다 지원):
    python -m src.main          # 프로젝트 루트에서 모듈로 실행 (권장)
    python src/main.py          # 파일을 직접 실행 (PyCharm '실행' 버튼 등)
"""
from __future__ import annotations

import sys
from pathlib import Path

# 파일을 직접 실행(python src/main.py)하면 프로젝트 루트가 sys.path에
# 자동으로 잡히지 않아 'src' 패키지를 못 찾는 경우가 있다.
# 이 스크립트가 패키지의 일부로 실행된 게 아니라면(=직접 실행) 프로젝트
# 루트를 sys.path 맨 앞에 넣어 'python -m' 없이도 동작하게 만든다.
if __package__ in (None, ""):
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
