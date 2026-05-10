import os
import requests

from dotenv import load_dotenv

load_dotenv()


def send_slack_alert(
    comparison,
    report_url,
    drift_result=None
):

    webhook_url = os.getenv(
        "SLACK_WEBHOOK_URL"
    )

    severity = comparison["severity"]

    if severity == "ok":

        print(
            "No Slack alert needed."
        )

        return

    status_map = {
        "ok": "PASS ✅",
        "warning": "WARN ⚠️",
        "critical": "FAIL 🚨"
    }

    status = status_map.get(
        severity,
        "UNKNOWN"
    )

    previous_accuracy = round(
        comparison["previous_accuracy"] * 100,
        2
    )

    current_accuracy = round(
        comparison["current_accuracy"] * 100,
        2
    )

    accuracy_delta = round(
        comparison["accuracy_delta"] * 100,
        2
    )

    regressions_count = len(
        comparison["regressions"]
    )

    improvements_count = len(
        comparison["improvements"]
    )

    message = f"""
*LLM Evaluation Alert*

Status: {status}

Accuracy:
{previous_accuracy}% → {current_accuracy}%

Delta:
{accuracy_delta}%

Regressions:
{regressions_count}

Improvements:
{improvements_count}

Baseline Prompt:
{comparison['baseline_prompt']}

Candidate Prompt:
{comparison['candidate_prompt']}

Full Report:
{report_url}
"""

    if drift_result and drift_result["drift_detected"]:

        message += f"""

⚠️ Slow Drift Detected

7-run moving average:
{drift_result['moving_average']}
"""

    payload = {
        "text": message
    }

    response = requests.post(
        webhook_url,
        json=payload
    )

    if response.status_code != 200:

        raise Exception(
            f"Slack alert failed: "
            f"{response.text}"
        )

    print("Slack alert sent.")