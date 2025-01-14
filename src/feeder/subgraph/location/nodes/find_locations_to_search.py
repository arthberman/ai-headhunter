from feeder.models.location import LocationAPIResponse, LocationData
from feeder.subgraph.location.state import LocationSubGraphState
from feeder.utils.location import find_location, read_location_cache


def find_locations_to_search(state: LocationSubGraphState) -> LocationSubGraphState:
    job_location = state.job_location

    # Check cache first
    cached_response = read_location_cache(job_location)
    if cached_response:
        api_out_locations = LocationAPIResponse(
            success=cached_response.get("success", False),
            message=cached_response.get("message", ""),
            data=LocationData(items=cached_response.get("data", {}).get("items", [])),
        )
    else:
        # If not in cache, use API
        api_response = find_location(job_location)
        api_out_locations = LocationAPIResponse(
            success=api_response.get("success", False),
            message=api_response.get("message", ""),
            data=LocationData(items=api_response.get("data", {}).get("items", [])),
        )

    location_pairs = []
    if api_out_locations.success and api_out_locations.data:
        location_pairs = [(item.id, item.name) for item in api_out_locations.data.items]

    return {"api_out_locations": location_pairs}
