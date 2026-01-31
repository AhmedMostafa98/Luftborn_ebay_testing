"""
eBay Search Results Page Object
Handles interactions with the search results page and filtering
"""

from base_page import BasePage
from playwright.sync_api import Page
import logging

logger = logging.getLogger(__name__)


class EBaySearchResultsPage(BasePage):
    """Page Object for eBay Search Results Page"""

    # Selectors for search results
    RESULT_ITEMS = 'ul.srp-results div.su-card-container'
    RESULT_ITEMS_TITLES = "ul.srp-results div.su-card-container__header span.su-styled-text.primary"
    RESULT_COUNT_TEXT = 'h1.srp-controls__count-heading span:first-child'
    FILTER_PANEL = 'div.srp-rail__left'

    def __init__(self, page: Page):
        """
        Initialize eBay Search Results Page
        """
        super().__init__(page)

    def get_search_result_count(self) -> int:
        """
        Get the number of search results
        """
        logger.info("Getting search result count")

        try:
            # Get the result count text
            count_text = self.get_text(self.RESULT_COUNT_TEXT)
            logger.info(f"Result count text: {count_text}")

            # Extract number from text like "1,023 results" or "Results for mazda mx-5"
            import re
            numbers = re.findall(r'\d+', count_text.replace(',', ''))

            if numbers:
                result_count = int(numbers[0])
                logger.info(f"Total search results: {result_count}")
                return result_count
            else:
                logger.warning(f"Could not extract count from text: {count_text}")
                return 0

        except Exception as e:
            logger.error(f"Error getting result count: {str(e)}")
            return 0

    def are_search_results_displayed(self) -> bool:
        """
        Check if search results are displayed
        """
        logger.info("Validating search results are displayed")

        try:
            # Wait for results to load
            results_visible = self.wait_for_element(self.RESULT_ITEMS, timeout=20000)

            if results_visible:
                # Count the number of results
                count = self.get_element_count(self.RESULT_ITEMS)
                logger.info(f"Found {count} result items displayed")
                return count > 0
            else:
                logger.warning("No search results found")
                return False

        except Exception as e:
            logger.error(f"Error validating search results: {str(e)}")
            return False

    def get_displayed_result_count(self) -> int:
        """
        Get the number of results currently displayed on page
        """
        try:
            count = self.get_element_count(self.RESULT_ITEMS)
            logger.info(f"Results displayed on page: {count}")
            return count
        except Exception as e:
            logger.error(f"Error counting displayed results: {str(e)}")
            return 0

    def filter_by_transmission(self, transmission_type: str) -> bool:
        """
        Filter search results by transmission type
        """
        logger.info(f"Applying transmission filter: {transmission_type}")

        try:
            # Wait for filter panel to load
            if not self.wait_for_element(self.FILTER_PANEL, timeout=15000):
                logger.error("Filter panel did not load")
                return False

            # Try to find and click transmission filter section
            logger.info("Looking for Transmission filter section")
            self.scroll_to_bottom()
            self.wait_for_load_state("")

            # Try clicking transmission filter button to expand it
            try:
                transmission_section = self.page.get_by_text("Transmission")
                if transmission_section.count() > 0:
                    transmission_section.first.click()
                    logger.info("Clicked Transmission filter to expand")
                    self.wait_for_load_state("domcontentloaded")
            except Exception as e:
                logger.warning(f"Could not expand transmission filter button: {str(e)}")

            # Find and click the specific transmission option
            logger.info(f"Looking for {transmission_type} option")
            option_locator = self.page.get_by_text(transmission_type)

            if option_locator.count() > 0:
                option_locator.first.click()
                logger.info(f"Selected {transmission_type} transmission option")
                self.wait_for_load_state("")
                logger.info("Filter applied successfully")
                return True
            else:
                logger.warning(f"{transmission_type} option not found in filter")
                return False

        except Exception as e:
            logger.error(f"Error applying transmission filter: {str(e)}")
            return False

    def get_result_titles(self, limit: int = 10) -> list:
        """
        Get titles of search results

        Args:
            limit (int): Maximum number of titles to retrieve

        Returns:
            list: List of result titles
        """
        logger.info(f"Getting result titles (limit: {limit})")

        try:
            titles = []
            result_items = self.page.locator(self.RESULT_ITEMS)
            count = result_items.count()

            for i in range(min(limit, count)):
                try:
                    # Get title from each result
                    title = self.page.locator(self.RESULT_ITEMS_TITLES).first.text_content()
                    if title:
                        titles.append(title.strip())
                except Exception as e:
                    logger.warning(f"Could not get title for result {i}: {str(e)}")

            logger.info(f"Retrieved {len(titles)} result titles")
            return titles

        except Exception as e:
            logger.error(f"Error getting result titles: {str(e)}")
            return []

    def validate_results_contain_keyword(self, keyword: str) -> bool:
        """
        Validate that search results contain a specific keyword

        Args:
            keyword (str): Keyword to search for in results

        Returns:
            bool: True if results contain the keyword, False otherwise
        """
        logger.info(f"Validating results contain keyword: {keyword}")

        try:
            titles = self.get_result_titles(limit=20)
            keyword_lower = keyword.lower()

            matching_results = [t for t in titles if keyword_lower in t.lower()]

            if matching_results:
                logger.info(f"Found {len(matching_results)} results containing '{keyword}'")
                return True
            else:
                logger.warning(f"No results containing '{keyword}' found")
                return False

        except Exception as e:
            logger.error(f"Error validating keyword in results: {str(e)}")
            return False

    def validate_results_and_count(self, keyword: str = None) -> int:
        """
        High-level helper: validate that results are displayed, optionally verify keyword, and return total count

        Args:
            keyword (str, optional): Keyword to validate within result titles

        Returns:
            int: Total search result count (0 if not displayed)
        """
        if not self.are_search_results_displayed():
            return 0

        count = self.get_search_result_count()
        if keyword:
            # validation performed but not enforced here
            try:
                self.validate_results_contain_keyword(keyword)
            except Exception:
                logger.warning("Keyword validation raised an exception but continuing to return count")
        return count

    def apply_transmission_and_get_count(self, transmission_type: str) -> int:
        """
        High-level helper: apply transmission filter and return filtered count

        Args:
            transmission_type (str): e.g. 'Manual'

        Returns:
            int: Filtered result count (0 if filter not applied)
        """
        applied = self.filter_by_transmission(transmission_type)
        if not applied:
            return 0

        # Wait for results to refresh and return new count
        self.wait_for_load_state("")
        return self.get_search_result_count()
