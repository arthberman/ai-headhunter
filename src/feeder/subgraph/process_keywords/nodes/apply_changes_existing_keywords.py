from src.feeder.subgraph.process_keywords.state import KeywordsState
from src.feeder.utils.logger_setup import logger


def apply_changes_existing_keywords(state: KeywordsState) -> KeywordsState:
    """Apply changes to existing keywords.

    Args:
        state: The state of the keywords subgraph.

    Returns:
        The state of the keywords subgraph.
    """
    try:
        logger.info("Applying changes to existing keywords")
        if not state.feedback_judge or not state.json_object:
            return state

        current_keywords = state.json_object.keywords
        anomalies = state.feedback_judge.anomalies
        keywords_to_remove = {anomaly.title for anomaly in anomalies}

        updated_keywords = [
            keyword for keyword in current_keywords if keyword not in keywords_to_remove
        ]

        state.json_object.keywords = updated_keywords
        logger.info(f"Updated keywords: {updated_keywords}")
        return state
    except Exception as e:
        logger.error(f"Error in apply_changes_existing_keywords: {e}")
        raise e
