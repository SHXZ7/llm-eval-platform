import os
import matplotlib.pyplot as plt
from jinja2 import Environment
from jinja2 import FileSystemLoader

from datetime import datetime


def generate_trend_chart(
    historical_scores,
    output_path
):

    plt.figure(figsize=(8, 4))

    plt.plot(historical_scores)

    plt.xlabel("Run")

    plt.ylabel("Accuracy")

    plt.title("Accuracy Trend")

    os.makedirs(
        "outputs/reports",
        exist_ok=True
    )

    plt.savefig(output_path)

    plt.close()


def generate_report(
    comparison,
    previous_results,
    current_results,
    prompt_config,
    drift_result=None
):

    env = Environment(
        loader=FileSystemLoader(
            "templates"
        )
    )

    template = env.get_template(
        "report_template.html"
    )

    regressions_data = []

    previous_map = {
        r.case_id: r
        for r in previous_results
    }

    current_map = {
        r.case_id: r
        for r in current_results
    }

    for case_id in comparison["regressions"]:

        old = previous_map[case_id]
        new = current_map[case_id]

        regressions_data.append({

            "case_id": case_id,

            "expected":
                old.expected_category,

            "old_prediction":
                old.predicted_category,

            "new_prediction":
                new.predicted_category
        })

    chart_path = (
        "outputs/reports/trend.png"
    )

    generate_trend_chart(
        historical_scores=[
            comparison["previous_accuracy"],
            comparison["current_accuracy"]
        ],
        output_path=chart_path
    )

    html = template.render(

        baseline_prompt=
            comparison["baseline_prompt"],

        candidate_prompt=
            comparison["candidate_prompt"],

        model=
            prompt_config.model,

        timestamp=
            datetime.now(),

        severity=
            comparison["severity"],

        previous_accuracy=
            comparison["previous_accuracy"],

        current_accuracy=
            comparison["current_accuracy"],

        accuracy_delta=
            comparison["accuracy_delta"],

        regressions=
            regressions_data,

        chart_path=
            "trend.png",

        drift_detected=
            drift_result.get("drift_detected", False) if drift_result else False,

        moving_average=
            drift_result.get("moving_average", 0) if drift_result else 0
    )

    report_path = (
        "outputs/reports/"
        "latest_report.html"
    )

    os.makedirs(
        "outputs/reports",
        exist_ok=True
    )

    with open(report_path, "w") as f:
        f.write(html)

    return report_path