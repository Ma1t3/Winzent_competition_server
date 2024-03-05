def analyze_load(data):
    total = len(data)

    if total == 0:  # should never be the case
        return 100

    sum = 0
    for load in data:
        sum += load.scaling

    return (sum / total) * 100
