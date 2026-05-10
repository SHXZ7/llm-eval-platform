import json
import sys
import os
import matplotlib.pyplot as plt

from app.models.schemas import EvalResult
from app.evals.comparator import compare_runs

from app.evals.config_loader import (
    load_thresholds
)

from app.llm.classifier import load_prompt

from app.reporting.report_generator import (
    generate_report
)

from app.alerting.slack_alert import (
    send_slack_alert
)

from app.evals.history_loader import (
    load_historical_accuracies
)

from app.evals.drift_detector import (
    detect_slow_drift
)


baseline_path = (
    "baselines/baseline_v1.json"
)

with open(baseline_path) as f:

    previous_data = json.load(f)


candidate_path = (
    "outputs/eval_runs/eval_v2.json"
)

with open(candidate_path) as f:

    current_data = json.load(f)


old_results = [
    EvalResult(**item)
    for item in previous_data
]

new_results = [
    EvalResult(**item)
    for item in current_data
]


thresholds = load_thresholds(
    "configs/thresholds.yaml"
)

prompt_config = load_prompt(
    "app/llm/prompts/v1.yaml"
)

comparison = compare_runs(

    previous_results=old_results,

    current_results=new_results,

    thresholds=thresholds,

    baseline_prompt="v1",

    candidate_prompt="v2"
)

print(comparison)
print()

report_path = generate_report(
    comparison=comparison,
    previous_results=old_results,
    current_results=new_results,
    prompt_config=prompt_config,
    drift_result=None
)

print(f"Report saved to {report_path}")

report_url = (
    "http://localhost:5500/"
    "outputs/reports/latest_report.html"
)

print()

historical_accuracies = (
    load_historical_accuracies()
)

drift_result = detect_slow_drift(

    historical_accuracies=
        historical_accuracies,

    thresholds=thresholds
)

print(drift_result)
print()

# Re-generate report with drift info
report_path = generate_report(
    comparison=comparison,
    previous_results=old_results,
    current_results=new_results,
    prompt_config=prompt_config,
    drift_result=drift_result
)

print(f"Report updated: {report_path}")

# Send Slack alert with drift info
send_slack_alert(
    comparison=comparison,
    report_url=report_url,
    drift_result=drift_result
)

if comparison["severity"] == "critical":

    print(
        "Critical regression detected."
    )

    sys.exit(1)