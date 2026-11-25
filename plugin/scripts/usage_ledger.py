"""轻量模型调用账本；仅记录时间、模型、用量和结果，不存对话内容。"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import time


@dataclass
class Attempt:
    root: Path
    purpose: str
    conversation_id: str
    provider: str
    model: str
    started_at: float = field(default_factory=time.monotonic)
    finished: bool = False

    def finish(self, status: str, usage: dict | None = None) -> None:
        if self.finished:
            return
        self.finished = True
        now = datetime.now(timezone.utc)
        day = now.strftime("%Y-%m-%d")
        path = self.root / "usage" / f"{day}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "time": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "purpose": self.purpose,
            "conversation_id": self.conversation_id,
            "provider": self.provider,
            "model": self.model,
            "status": status,
            "duration_ms": int((time.monotonic() - self.started_at) * 1000),
            "usage": usage or {},
        }
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")


def record_attempt(root: Path, purpose: str, conversation_id: str, config: dict) -> Attempt:
    return Attempt(
        root=root,
        purpose=purpose,
        conversation_id=conversation_id,
        provider=str(config.get("provider") or "agy"),
        model=str(config.get("model") or ""),
    )


def usage_report(root: Path, days: int = 30) -> dict:
    usage_dir = root / "usage"
    if not usage_dir.is_dir():
        return {"days": [], "totals": {}, "by_model": {}}
    files = sorted(usage_dir.glob("*.jsonl"))[-days:]
    totals = {
        "attempts": 0,
        "completed": 0,
        "failed": 0,
        "input_tokens": 0,
        "cache_read_tokens": 0,
        "output_tokens": 0,
        "thinking_tokens": 0,
        "total_tokens": 0,
        "unknown_usage_attempts": 0,
    }
    by_model: dict[str, dict] = {}
    for file_path in files:
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except ValueError:
                continue
            key = f"{item.get('provider', 'agy')}:{item.get('model', 'unknown')}"
            bucket = by_model.setdefault(key, {
                "attempts": 0, "completed": 0, "failed": 0,
                "input_tokens": 0, "cache_read_tokens": 0,
                "output_tokens": 0, "thinking_tokens": 0, "total_tokens": 0,
            })
            for target in (totals, bucket):
                target["attempts"] += 1
                if item.get("status") == "completed":
                    target["completed"] += 1
                else:
                    target["failed"] += 1
            usage = item.get("usage") or {}
            if not usage or not any(isinstance(usage.get(k), int) for k in ("input_tokens", "output_tokens", "total_tokens")):
                totals["unknown_usage_attempts"] += 1
                continue
            for field_name in ("input_tokens", "cache_read_tokens", "output_tokens", "thinking_tokens", "total_tokens"):
                val = usage.get(field_name)
                if isinstance(val, int) and val >= 0:
                    totals[field_name] += val
                    bucket[field_name] += val
    return {
        "days": [f.stem for f in files],
        "totals": totals,
        "by_model": by_model,
    }
