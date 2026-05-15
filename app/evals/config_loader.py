import os
import yaml


def load_thresholds(path):
    """
    Load thresholds from YAML file with environment variable overrides.
    
    Environment variables take precedence over YAML defaults:
    - WARNING_DELTA: Warning threshold for metric delta
    - CRITICAL_DELTA: Critical threshold for metric delta
    - DRIFT_WINDOW_SIZE: Window size for drift detection
    - DRIFT_THRESHOLD: Threshold for drift detection
    """
    with open(path, "r") as file:
        thresholds = yaml.safe_load(file)
    
    # Allow environment variable overrides
    # Priority: ENV vars > YAML file > hardcoded defaults
    thresholds["warning_delta"] = float(
        os.getenv("WARNING_DELTA", thresholds.get("warning_delta", 0.03))
    )
    thresholds["critical_delta"] = float(
        os.getenv("CRITICAL_DELTA", thresholds.get("critical_delta", 0.08))
    )
    thresholds["drift_window_size"] = int(
        os.getenv("DRIFT_WINDOW_SIZE", thresholds.get("drift_window_size", 7))
    )
    thresholds["drift_threshold"] = float(
        os.getenv("DRIFT_THRESHOLD", thresholds.get("drift_threshold", 0.90))
    )
    
    return thresholds
