#!/usr/bin/env python3
"""Compatibility entry point for validate-final-ipa.py."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("validate-final-ipa.py")), run_name="__main__")
