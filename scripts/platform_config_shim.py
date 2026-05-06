# scripts/platform_config_shim.py
"""Minimal replacement for workflow.automation.platform_config"""

import os

# Paths that the scripts need
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
_QUAKECW = os.path.dirname(_SCRIPTS_DIR)  # one level up from scripts

GMSIM_TEMPLATES_DIR = os.path.join(_QUAKECW, "gmsim_templates")
VELOCITY_MODEL_DIR = os.environ.get("VELOCITY_MODEL_DIR", "")

if VELOCITY_MODEL_DIR is None:
    print("ERROR: VELOCITY_MODEL_DIR is not set.", file=sys.stderr)
    print("Ensure quakecw_config.sh was sourced before running.", file=sys.stderr)
    sys.exit(1)


# Build the dictionary in the same format as the original
platform_config = {
    "GMSIM_TEMPLATES_DIR": GMSIM_TEMPLATES_DIR,
    "VELOCITY_MODEL_DIR": VELOCITY_MODEL_DIR,
    "DEFAULT_SITE_RESPONSE_DIR": os.path.join(
        GMSIM_TEMPLATES_DIR, "site_response"
    ),
}
