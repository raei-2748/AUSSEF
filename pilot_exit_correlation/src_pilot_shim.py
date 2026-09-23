"""Shim so other projects can reuse the pilot's hash-verified network loader without a package-name clash."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("pilot_inputs", Path(__file__).resolve().parent / "src" / "inputs.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
load_network = _mod.load_network
load_communities = _mod.load_communities
sha256 = _mod.sha256
