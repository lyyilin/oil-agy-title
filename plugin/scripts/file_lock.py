"""跨平台非阻塞内核文件锁；进程退出后自动释放。"""
from __future__ import annotations

import os
import sys

if sys.platform == "win32":
    import msvcrt

    def acquire(stream) -> None:
        stream.seek(0)
        try:
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise BlockingIOError("locked") from exc

    def release(stream) -> None:
        try:
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
else:
    import fcntl

    def acquire(stream) -> None:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def release(stream) -> None:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
