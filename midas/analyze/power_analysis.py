import numpy as np
from natsort import natsorted


def analyze_power(data, step_size):
    # analyze loads/gens/extgrid
    ef = step_size / 3_600
    data = data[natsorted(data.columns)]

    # Aggregated analyis
    total_p = data["p_mw"].sum()
    total_q = data["q_mvar"].sum()

    total_s = np.sqrt(
        np.square(total_p.sum() * ef) + np.square(total_q.sum() * ef)
    )

    return total_p, total_q, total_s
