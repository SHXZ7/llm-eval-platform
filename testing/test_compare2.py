import json

from app.models.schemas import EvalResult
from app.evals.comparator import compare_runs

from app.evals.config_loader import (
    load_thresholds
)

from app.llm.classifier import load_prompt

from app.reporting.report_generator import (
    generate_report
)


with open(
    "outputs/eval_runs/eval_v1.json"
) as f:

    old_data = json.load(f)


with open(
    "outputs/eval_runs/eval_v2.json"
) as f:

    new_data = json.load(f)


old_results = [
    EvalResult(**item)
    for item in old_data
]

new_results = [
    EvalResult(**item)
    for item in new_data
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
    prompt_config=prompt_config
)

print(f"Report saved to {report_path}")
