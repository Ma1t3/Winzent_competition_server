def analyze_buses(data):
    fails = 0
    total = len(data)

    if total == 0:  # should never be the case
        score = 100
    else:
        for bus in data:
            fails += _voltage_violation_report(bus.vm_pu)

        score = 100 * (1.0 - (fails / total))

    return score


def _voltage_violation_report(vm_pus):
    too_high4 = vm_pus > 1.04
    too_low4 = vm_pus < 0.96

    return too_low4 + too_high4
