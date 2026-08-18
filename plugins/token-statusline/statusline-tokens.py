#!/usr/bin/env python3
"""Compact token-usage status line for CodeBuddy Code (statusLine command).

Reads the JSON statusLine payload from stdin and prints a single compact line:

    ~/repo (branch) ↑45k ↓1k R4.6M CH94.2% 23.6%/192k (auto)

All token fields reflect the CURRENT context window state (so they shrink after
a /compact or context-compression), sourced from the payload's
`context_window.current_usage`. Falls back to parsing the transcript JSONL when
the payload omits that data.

  ↑   fresh (non-cached) input tokens currently in the context window
  ↓   output tokens of the current context
  R   cache-read tokens (session cumulative) — how much was served from cache
  CH  cache-hit ratio = cache_read / (fresh + cache_read + cache_creation) * 100
  X%  current context-window usage % (payload context_window.used_percentage)
  /Y  context window size (payload context_window_size; default 1.0M)
  (mode)  permission_mode from the payload (falls back to output_style.name)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

# Model id -> context window size (tokens), used only if the payload omits it.
MODEL_CONTEXT = {
    "hy3": 1_000_000,
    "claude-3-5-sonnet": 200_000,
    "claude-3-5-sonnet-20241022": 200_000,
    "claude-3-7-sonnet": 200_000,
    "claude-sonnet-4": 200_000,
    "claude-opus-4": 200_000,
    "gpt-4o": 128_000,
    "gpt-5": 400_000,
}


def fmt_tokens(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}k"
    return str(n)


def extract_usage(entry):
    pd = entry.get("providerData") or {}
    usage = entry.get("usage") or pd.get("usage") or entry.get("costData") or {}
    if not usage:
        return None
    in_t = usage.get("inputTokens") or usage.get("input_tokens") or 0
    out_t = usage.get("outputTokens") or usage.get("output_tokens") or 0
    cr = 0
    for d in usage.get("inputTokensDetails") or []:
        if isinstance(d, dict):
            cr += d.get("cached_tokens", 0) or 0
    if cr == 0:
        cr = usage.get("cacheReadTokens") or usage.get("cache_read_input_tokens") or 0
    cw = usage.get("cacheWriteTokens") or usage.get("cache_creation_input_tokens") or 0
    return {"in": in_t, "out": out_t, "cr": cr, "cw": cw}


def transcript_totals(transcript):
    """Fallback: sum token usage across the session transcript JSONL."""
    totals = {"in": 0, "out": 0, "cr": 0, "cw": 0}
    paths = []
    if transcript:
        p = Path(transcript)
        if p.exists():
            paths.append(p)
    if not paths:
        for h in (Path.home() / ".codebuddy" / "projects",
                  Path.home() / ".claude" / "projects"):
            if h.exists():
                paths.extend(h.rglob("*.jsonl"))
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    u = extract_usage(obj)
                    if not u:
                        continue
                    totals["in"] += u["in"]
                    totals["out"] += u["out"]
                    totals["cr"] += u["cr"]
                    totals["cw"] += u["cw"]
        except OSError:
            continue
    return totals


def main():
    payload = {}
    try:
        raw = sys.stdin.read()
        if raw.strip():
            payload = json.loads(raw)
    except Exception:
        payload = {}

    transcript = payload.get("transcript_path") or ""
    model_id = (payload.get("model") or {}).get("id") or "hy3"
    # Show the permission mode (falls back to output_style.name if absent)
    mode = payload.get("permission_mode") \
        or (payload.get("output_style") or {}).get("name") \
        or "auto"

    # Authoritative context-window data reported in the payload.
    ctx = payload.get("context_window") or {}
    cw_size = ctx.get("context_window_size") or MODEL_CONTEXT.get(model_id, 1_000_000)
    used_pct = ctx.get("used_percentage")

    # Current-context token composition (drops after compression).
    cu = ctx.get("current_usage") or {}
    cur_in = cu.get("input_tokens") or 0
    cur_out = cu.get("output_tokens") or 0
    cur_cr = cu.get("cache_read_input_tokens") or 0
    cur_cw = cu.get("cache_creation_input_tokens") or 0

    # Fallback to lifetime transcript totals if the payload lacks current_usage.
    if not (cur_in or cur_out or cur_cr or cur_cw):
        t = transcript_totals(transcript)
        cur_in = max(0, t["in"] - t["cr"] - t["cw"])
        cur_out = t["out"]
        cur_cr = t["cr"]
        cur_cw = t["cw"]

    direct = cur_in if cur_in > 0 else 0
    denom = cur_in + cur_cr + cur_cw
    ch = (cur_cr / denom * 100) if denom > 0 else 0.0

    # Context-window usage % comes from the payload; fall back to an estimate
    # (fresh tokens / window size) only if the payload omits it.
    if used_pct is None:
        used_pct = (direct / cw_size * 100) if cw_size > 0 else 0.0
    ctx_pct = used_pct

    # Working directory (home shortened to ~) + current git branch
    cwd = (payload.get("workspace") or {}).get("current_dir") or ""
    short_cwd = cwd
    home = os.path.expanduser("~")
    if home and cwd.startswith(home):
        short_cwd = "~" + cwd[len(home):]
    branch = ""
    if cwd:
        try:
            r = subprocess.run(["git", "-C", cwd, "branch", "--show-current"],
                               capture_output=True, text=True, timeout=2)
            if r.returncode == 0:
                b = r.stdout.strip()
                if b:
                    branch = b
        except Exception:
            branch = ""
    prefix = f"{short_cwd} ({branch})" if branch else short_cwd

    line = (f"{prefix}\n"
            f"\u2191{fmt_tokens(direct)} \u2193{fmt_tokens(cur_out)} "
            f"R{fmt_tokens(cur_cr)} CH{ch:.1f}%   "
            f"{ctx_pct:.1f}%/{fmt_tokens(cw_size)} ({mode})")
    sys.stdout.write(line)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # never break the status bar
        sys.stdout.write(f"(statusline error: {exc})")
