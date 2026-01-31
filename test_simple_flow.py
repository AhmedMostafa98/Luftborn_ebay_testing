import json
from pathlib import Path
from home_page import EBayHomePage
from search_results_page import EBaySearchResultsPage

def load_config():
    cfg_path = Path(__file__).resolve().parent / "config.json"
    with open(cfg_path, 'r') as f:
        return json.load(f)


def test_search_and_filter(page):
    """Simple test that delegates all work to page-level helpers"""
    config = load_config()
    search_term = config["test_data"]["search_term"]
    transmission = config["test_data"]["filters"]["transmission"]

    home = EBayHomePage(page)
    home.navigate_to_home()
    home.search_for_item(search_term)

    results = EBaySearchResultsPage(page)

    # Validate results and get count
    count = results.validate_results_and_count(search_term)
    assert count > 0, f"Expected search results > 0 for '{search_term}'"

    # Apply filter and verify filtered count is <= original
    filtered_count = results.apply_transmission_and_get_count(transmission)
    assert filtered_count >= 0
    assert filtered_count <= count
