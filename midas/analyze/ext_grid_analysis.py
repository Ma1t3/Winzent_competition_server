def analyze_ext_grid(data):
    fails = 0
    total = len(data)

    if total == 0:  # should never be the case
        score = 100
    else:
        sum_ext_grid = 0
        counter_ext_grid = 1
        amount_ext_grid = 1

        # get the amount of trafos
        for ext_grid in data:
            if ext_grid.pp_index >= amount_ext_grid:
                amount_ext_grid += 1

        for ext_grid in data:
            # Sum up all extgrid values for one step then check violation. Then start again.
            if counter_ext_grid % amount_ext_grid == 0:
                counter_ext_grid = 1
                sum_ext_grid += abs(ext_grid.p_mw)
                fails += _violation_report(sum_ext_grid)
                sum_ext_grid = 0
            else:
                counter_ext_grid += 1
                sum_ext_grid += abs(ext_grid.p_mw)

        # The total amount gets smaller depending on how many ext grids there are.
        score = 100 * (1.0 - (fails / (total / amount_ext_grid)))

    return score


def _violation_report(p_mws):
    fail = 0

    # We observed the maximum value for bhv powernet and adjusted the function accordingly.
    # Another powernet may need another function.
    # (x-2)*0.05
    fail += (p_mws - 2) * 0.05
    if fail < 0:
        fail = 0
    if fail > 1:
        fail = 1

    return fail
