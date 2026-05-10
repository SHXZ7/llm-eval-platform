import json
import glob


def load_historical_accuracies():

    files = sorted(
        glob.glob(
            "outputs/eval_runs/*.json"
        )
    )

    accuracies = []

    for file_path in files:

        with open(file_path) as f:

            results = json.load(f)

        total = len(results)

        correct = sum(
            r["category_correct"]
            for r in results
        )

        accuracy = correct / total

        accuracies.append(accuracy)

    return accuracies