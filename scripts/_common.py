# -*- coding: utf-8 -*-
"""
genslides · shared helpers for the Python script layer (cross-platform).
Canonical implementations live in .py; the .ps1 files are thin Windows wrappers.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ENV_PATH = os.path.join(ROOT, "config", "env.json")


def utf8_stdout():
    """GBK consoles (Windows) choke on the Chinese in themes/output — force utf-8."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except (AttributeError, ValueError):
            pass


def load_env():
    if not os.path.exists(ENV_PATH):
        sys.exit("config/env.json not found — run `python scripts/setup.py` first")
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def need(env, key):
    p = env.get(key)
    if not p or not os.path.exists(p):
        sys.exit("%s not found at %r — edit config/env.json (or rerun scripts/setup.py)" % (key, p))
    return p


def run(cmd, **kw):
    """Run a command, return (rc, combined output). Never raises on nonzero exit."""
    kw.setdefault("stdout", subprocess.PIPE)
    kw.setdefault("stderr", subprocess.STDOUT)
    env = kw.pop("extra_env", None)
    if env:
        full = dict(os.environ)
        full.update(env)
        kw["env"] = full
    try:
        p = subprocess.run(cmd, **kw)
        return p.returncode, (p.stdout or b"").decode("utf-8", "replace")
    except FileNotFoundError as e:
        return 127, str(e)
