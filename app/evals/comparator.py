from collections import defaultdict


def calculate_accuracy(results):

    total = len(results)

    correct = sum(
        r.category_correct
        for r in results
    )

    return correct / total


def category_breakdown(results):

    stats = defaultdict(
        lambda: {
            "correct": 0,
            "total": 0
        }
    )

    for result in results:

        category = result.expected_category

        stats[category]["total"] += 1

        if result.category_correct:
            stats[category]["correct"] += 1

    breakdown = {}

    for category, values in stats.items():

        breakdown[category] = (
            values["correct"] /
            values["total"]
        )

    return breakdown


def determine_severity(
    accuracy_delta,
    thresholds
):

    delta = abs(accuracy_delta)

    if delta >= thresholds["critical_delta"]:
        return "critical"

    if delta >= thresholds["warning_delta"]:
        return "warning"

    return "ok"


def compare_runs(
    previous_results,
    current_results,
    thresholds,
    baseline_prompt,
    candidate_prompt
):

    previous_map = {
        result.case_id: result
        for result in previous_results
    }

    current_map = {
        result.case_id: result
        for result in current_results
    }

    regressions = []
    improvements = []

    for case_id in current_map:

        prev = previous_map.get(case_id)
        curr = current_map.get(case_id)

        if not prev or not curr:
            continue

        # PASS → FAIL
        if (
            prev.category_correct
            and not curr.category_correct
        ):
            regressions.append(case_id)

        # FAIL → PASS
        if (
            not prev.category_correct
            and curr.category_correct
        ):
            improvements.append(case_id)

    previous_accuracy = calculate_accuracy(
        previous_results
    )

    current_accuracy = calculate_accuracy(
        current_results
    )

    accuracy_delta = (
        current_accuracy -
        previous_accuracy
    )

    previous_breakdown = category_breakdown(
        previous_results
    )

    current_breakdown = category_breakdown(
        current_results
    )

    severity = determine_severity(
        accuracy_delta,
        thresholds
    )

    return {
        "baseline_prompt": baseline_prompt,
        "candidate_prompt": candidate_prompt,
        "previous_accuracy": previous_accuracy,
        "current_accuracy": current_accuracy,
        "accuracy_delta": accuracy_delta,
        "severity": severity,
        "regressions": regressions,
        "improvements": improvements,
        "previous_category_scores": previous_breakdown,
        "current_category_scores": current_breakdown
    }