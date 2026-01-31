"""
eBay Home Page Object
Handles interactions with the eBay home page
"""

from base_page import BasePage
from playwright.sync_api import Page
import logging

logger = logging.getLogger(__name__)


class EBayHomePage(BasePage):
    """Page Object for eBay Home Page"""

    # Selectors
    SEARCH_INPUT = 'input[placeholder="Search for anything"]'
    SEARCH_BUTTON = 'button[type="submit"]'
    EBAY_LOGO = 'a[href="https://www.ebay.com/"]'

    def __init__(self, page: Page):
        super().__init__(page)
        self.page_url = "https://www.ebay.com/"

    def navigate_to_home(self) -> None:
        """Navigate to eBay home page"""
        self.navigate(self.page_url)
        logger.info("Navigated to eBay home page")

    def is_home_page_loaded(self) -> bool:
        """
        Validate that eBay home page is loaded
        """
        logger.info("Validating eBay home page is loaded")

        try:
            # Check if search input is visible
            search_visible = self.wait_for_element(self.SEARCH_INPUT, timeout=15000)

            if search_visible:
                logger.info("eBay home page loaded successfully")
                return True
            else:
                logger.warning("eBay home page did not load properly")
                return False

        except Exception as e:
            logger.error(f"Error validating home page: {str(e)}")
            return False

    def search_for_item(self, search_term: str) -> None:
        """
        Search for an item on eBay
        """
        logger.info(f"Searching for: {search_term}")

        try:
            # Ensure on home page
            if not self.is_home_page_loaded():
                self.navigate_to_home()

            # Fill search input
            self.fill(self.SEARCH_INPUT, search_term)
            logger.info(f"Entered search term: {search_term}")

            # Click search button
            self.click(self.SEARCH_BUTTON)
            logger.info("Clicked search button")

            # Wait for results page to load
            self.wait_for_load_state("")
            logger.info("Search results page loaded")

        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            raise

    def get_page_header_text(self) -> str:
        """
        Get the header text from home page
        """
        try:
            header_text = self.get_text("body > header")
            logger.info(f"Header text: {header_text}")
            return header_text
        except Exception as e:
            logger.error(f"Error getting header text: {str(e)}")
            return ""
