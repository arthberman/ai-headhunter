from logging import getLogger

from src.feeder.models.location import LocationAPIResponse, LocationData
from src.feeder.subgraph.location.state import LocationSubGraphState
from src.feeder.utils.location import find_location, read_location_cache

logger = getLogger(__name__)


def find_locations_to_search(state: LocationSubGraphState) -> LocationSubGraphState:
    """Find and return location data from cache or API.

    Cache Strategy:
    - First attempts local JSON cache lookup
    - Falls back to API call if cache miss
    - API responses are automatically cached for future use

    Response Processing:
    - Converts raw API/cache data into (id, name) tuples
    """
    job_location = state.job_location

    # Check cache first
    cached_response = read_location_cache(job_location)
    if cached_response:
        logger.info("Cached response found")
        api_out_locations = LocationAPIResponse(
            success=cached_response.get("success", False),
            message=cached_response.get("message", ""),
            data=LocationData(items=cached_response.get("data", {}).get("items", [])),
        )
        logger.info(f"api_out_locations: {api_out_locations}")
    else:
        logger.info("Cached response not found")
        # If not in cache, use API
        api_response = find_location(job_location)
        api_out_locations = LocationAPIResponse(
            success=api_response.get("success", False),
            message=api_response.get("message", ""),
            data=LocationData(items=api_response.get("data", {}).get("items", [])),
        )

    location_pairs = []
    if api_out_locations.success and api_out_locations.data:
        logger.info(f"api_out_locations.data: {api_out_locations.data}")
        location_pairs = [(item.id, item.name) for item in api_out_locations.data.items]
        logger.info(f"location_pairs: {location_pairs}")
    return {"api_out_locations": location_pairs}
