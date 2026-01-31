"""
Base Page Object class providing common Playwright actions
"""

from playwright.sync_api import Page, Browser, BrowserContext
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BasePage:

    def __init__(self, page: Page):
        """
        Initialize BasePage with a Playwright Page object
        """
        self.page = page
        self.timeout = 30000  # Default timeout in milliseconds

    def navigate(self, url: str) -> None:
        """
        Navigate to a given URL
        """
        logger.info(f"Navigating to: {url}")
        self.page.goto(url)
        logger.info(f"Successfully navigated to: {url}")

    def click(self, selector: str) -> None:
        """
        Click on an element identified by selector
        """
        logger.info(f"Clicking element: {selector}")
        self.page.click(selector)

    def fill(self, selector: str, text: str) -> None:
        """
        Fill text input field
        """
        logger.info(f"Filling text into {selector}: {text}")
        self.page.fill(selector, text)

    def wait_for_element(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for element to be visible
        """
        timeout = timeout or self.timeout
        try:
            logger.info(f"Waiting for element: {selector}")
            self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Element not found: {selector} - {str(e)}")
            return False

    def is_element_visible(self, selector: str) -> bool:
        """
        Check if element is visible
        """
        try:
            return self.page.is_visible(selector)
        except Exception:
            return False

    def get_text(self, selector: str) -> str:
        """
        Get text content of an element
        """
        logger.info(f"Getting text from: {selector}")
        return self.page.text_content(selector) or ""

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Get attribute value of an element
        """
        logger.info(f"Getting attribute '{attribute}' from: {selector}")
        return self.page.get_attribute(selector, attribute)

    def press_key(self, key: str) -> None:
        """
        Press a keyboard key
        """
        logger.info(f"Pressing key: {key}")
        self.page.press("body", key)

    def take_screenshot(self, filename: str) -> None:
        """
        Take a screenshot of the current page
        """
        logger.info(f"Taking screenshot: {filename}")
        self.page.screenshot(path=filename)

    def get_page_title(self) -> str:
        """
        Get the page title
        """
        title = self.page.title()
        logger.info(f"Page title: {title}")
        return title

    def get_page_url(self) -> str:
        """
        Get the current page URL
        """
        url = self.page.url
        logger.info(f"Current URL: {url}")
        return url

    def scroll_to_bottom(self) -> None:
        """Scroll to bottom of page"""
        logger.info("Scrolling to bottom of page")
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def scroll_to_element(self, selector: str) -> None:
        """
        Scroll to a specific element
        """
        logger.info(f"Scrolling to element: {selector}")
        self.page.locator(selector).scroll_into_view_if_needed()

    def wait_for_load_state(self, state: str = "domcontentloaded") -> None:
        """
        Wait for page load state
        Args:
            state (str): Load state ('domcontentloaded', 'load', 'networkidle')
        """
        logger.info(f"Waiting for load state: {state}")
        self.page.wait_for_load_state(state)

    def get_element_count(self, selector: str) -> int:
        """
        Get count of elements matching selector
        """
        count = self.page.locator(selector).count()
        logger.info(f"Found {count} elements matching: {selector}")
        return count

    def close_page(self) -> None:
        """Close the current page"""
        logger.info("Closing page")
        self.page.close()
