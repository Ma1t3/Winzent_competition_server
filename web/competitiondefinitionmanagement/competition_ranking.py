import logging
from typing import List, Tuple

from django.db import connections
from django.db.utils import DatabaseError

from pgasc.web.experimentdefinitionmanagement.models import ExperimentRun

logger = logging.getLogger(__name__)


def get_aggregated_results_for_experiments(
    experiment_ids,
) -> List[Tuple[str, float, float, float, str]]:
    """returns a list of tuples (one tuple for each evaluation criterion)
    of the form (name of the evaluation criterion / rating function, avg value, min value, max value, unit)"""
    try:
        with connections["midas"].cursor() as cursor:
            experiment_id_str = (
                f"({','.join(str(id) for id in experiment_ids)})"
            )
            cursor.execute(
                f"select name, avg(value), min(value), max(value), unit "
                f"FROM experiment_result  "
                f"WHERE experiment_id in {experiment_id_str} "
                f"GROUP BY name, unit "
                f"ORDER BY name "
            )
            results = cursor.fetchall()
            return results
    except DatabaseError as e:
        logger.error(e, exc_info=True)
        return []


def calculate_competition_results(competition, aggregate_by_defenders=True):
    """Returns the results of the competition in a dictionary with evaluation criteria as keys
    and list of result tuples (agent, avg value, min value, max value, unit) as values"""
    experiments = ExperimentRun.objects.filter(competition_id=competition.id)
    if aggregate_by_defenders:
        agents = competition.defender.all()
    else:
        agents = competition.attacker.all()

    competition_results = {}

    for agent in agents:
        # calculate the experiments in which the agent participated
        if aggregate_by_defenders:
            experiment_ids = experiments.filter(defender=agent).values_list(
                "pk", flat=True
            )
        else:
            experiment_ids = experiments.filter(attacker=agent).values_list(
                "pk", flat=True
            )

        # get the results for the experiments
        results = get_aggregated_results_for_experiments(experiment_ids)

        # save the results in the dictionary with the evaluation criteria as key
        for result in results:
            evaluation_criteria = result[0]
            result_tuple = (agent, *result[1:])
            if evaluation_criteria not in competition_results:
                competition_results[evaluation_criteria] = []
            competition_results[evaluation_criteria].append(result_tuple)
    return competition_results


def calculate_ranking(
    competition_results, evaluation_criteria: str, defender_ranking=True
):
    """Calculates the ranking of the competition results for the given evaluation criteria"""
    ranking = []
    for agent, *result in competition_results.get(evaluation_criteria, []):
        avg_value = result[0]
        ranking.append((agent, avg_value))
    ranking.sort(key=lambda x: x[1], reverse=defender_ranking)
    return ranking
