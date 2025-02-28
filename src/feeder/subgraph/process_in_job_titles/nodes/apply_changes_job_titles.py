from src.feeder.subgraph.process_in_job_titles.state import NewJobTitlesSubgraphState
from src.feeder.utils.logger_setup import logger


def apply_changes_job_titles(
    state: NewJobTitlesSubgraphState,
) -> NewJobTitlesSubgraphState:
    """Apply changes to job titles by removing heuristically identified titles mentioned in feedback."""
    try:
        logger.info("Applying changes to job titles")
        if not state.feedback_judge or not state.json_object:
            return state

        current_titles = state.json_object.in_job_titles
        anomalies = state.feedback_judge.anomalies
        titles_to_remove = {anomaly.title for anomaly in anomalies}

        updated_titles = [
            title for title in current_titles if title not in titles_to_remove
        ]

        state.json_object.in_job_titles = updated_titles
        logger.info(f"Updated job titles to include: {updated_titles}")
        return state
    except Exception as e:
        logger.error(f"Error in apply_changes_job_titles: {e}")
        raise e
