#!/usr/bin/env python3
"""从 Skill 目录动态定位插件主脚本 scripts/oil_agy_title.py 并原样转发参数。"""
from __future__ import annotations

from pathlib import Path
import runpy
import sys


def main() -> int:
    target = Path(__file__).resolve().parents[3] / "scripts" / "oil_agy_title.py"
    if not target.is_file():
        sys.stderr.write(f"未找到插件主脚本：{target}\n")
        return 1
    sys.path.insert(0, str(target.parent))
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
