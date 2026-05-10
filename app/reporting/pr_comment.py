def build_pr_comment(
    comparison
):

    severity = comparison["severity"]

    return f"""
# LLM Evaluation Report

Severity:
{severity}

Accuracy:
{comparison['previous_accuracy']:.2%}
→
{comparison['current_accuracy']:.2%}

Delta:
{comparison['accuracy_delta']:.2%}

Regressions:
{len(comparison['regressions'])}

Improvements:
{len(comparison['improvements'])}
"""