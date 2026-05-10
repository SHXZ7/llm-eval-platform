from statistics import mean


def detect_slow_drift(
    historical_accuracies,
    thresholds
):

    window_size = thresholds[
        "drift_window_size"
    ]

    drift_threshold = thresholds[
        "drift_threshold"
    ]

    if (
        len(historical_accuracies)
        < window_size
    ):

        return {
            "drift_detected": False,
            "moving_average": None
        }

    recent_window = historical_accuracies[
        -window_size:
    ]

    moving_average = mean(
        recent_window
    )

    drift_detected = (
        moving_average <
        drift_threshold
    )

    return {

        "drift_detected":
            drift_detected,

        "moving_average":
            round(moving_average, 4),

        "window":
            recent_window
    }