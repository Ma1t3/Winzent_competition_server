def analyze_line(data):
    fails = 0
    total = len(data)

    if total == 0:  # should never be the case
        score = 100
    else:
        for line in data:
            fails += _violation_report(line.loading_percent)

        score = 100 * (1.0 - (fails / total))

    return score


def _violation_report(loading_percent):
    fails = 0
    # The values may be changed in the future.
    if loading_percent > 80:
        fails += 1
    elif loading_percent > 50:
        fails += 0.5

    return fails
