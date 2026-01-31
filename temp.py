"""
eBay Automation Framework - Main Test Execution Script
Orchestrates the complete user flow automation for eBay search and filtering
"""

import json
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright
from base_page import BasePage
from home_page import EBayHomePage
from search_results_page import EBaySearchResultsPage
from logger_report import TestLogger, TestReport


class EBayAutomationFramework:
    """Main automation framework for eBay test scenarios"""

    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the automation framework

        Args:
            config_file (str): Path to configuration file
        """
        self.config = self.load_config(config_file)
        self.logger = TestLogger.setup_logger(
            self.config["logging"]["log_file"],
            self.config["logging"]["log_level"]
        )
        self.report = TestReport(self.config["logging"]["report_file"])
        self.logger.info("eBay Automation Framework initialized")

    @staticmethod
    def load_config(config_file: str) -> dict:
        """
        Load configuration from JSON file

        Args:
            config_file (str): Path to configuration file

        Returns:
            dict: Configuration dictionary
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"Configuration loaded from: {config_file}")
            return config
        except FileNotFoundError:
            print(f"Configuration file not found: {config_file}")
            raise
        except json.JSONDecodeError as e:
            print(f"Error parsing configuration file: {str(e)}")
            raise

    def run_automation(self) -> bool:
        """
        Run the complete automation workflow

        Returns:
            bool: True if all steps passed, False otherwise
        """
        self.logger.info("=" * 80)
        self.logger.info("Starting eBay Automation Test Flow")
        self.logger.info("=" * 80)

        playwright = None
        browser = None
        context = None
        success = True

        try:
            # Start Playwright
            playwright = sync_playwright().start()
            self.logger.info("Playwright started")

            # Launch browser
            self.logger.info("Launching Chromium browser")
            browser_config = self.config.get("browser_config", {})
            browser = playwright.chromium.launch(
                headless=browser_config.get("headless", False),
                slow_mo=browser_config.get("slow_mo", 500)
            )
            self.logger.info("Browser launched successfully")

            # Create browser context and page
            context = browser.new_context()
            page = context.new_page()
            self.logger.info("Browser page created")

            # Step 1: Navigate to eBay home page
            home_page = EBayHomePage(page)
            home_page.navigate_to_home()

            # Step 2: Validate home page is loaded
            if home_page.is_home_page_loaded():
                self.report.add_result(
                    "Validate eBay home page loaded",
                    "PASS",
                    "eBay home page validated successfully"
                )
                self.logger.info("eBay home page validated successfully")
            else:
                self.report.add_result(
                    "Validate eBay home page loaded",
                    "FAIL",
                    "Failed to validate eBay home page"
                )
                self.logger.error("Home page validation failed")
                success = False

            # Step 3: Search for the test item
            search_term = self.config["test_data"]["search_term"]
            home_page.search_for_item(search_term)

            # Step 4: Validate search results are displayed
            search_page = EBaySearchResultsPage(page)
            if search_page.are_search_results_displayed():
                self.report.add_result(
                    "Validate search results displayed",
                    "PASS",
                    "Search results are displayed on the page"
                )
                self.logger.info("Search results validated")
            else:
                self.report.add_result(
                    "Validate search results displayed",
                    "FAIL",
                    "No search results were displayed"
                )
                self.logger.error("No results displayed")
                success = False

            # Step 5: Get and log result count
            result_count = search_page.get_search_result_count()

            if result_count > 0:
                self.report.add_result(
                    "Get search result count",
                    "PASS",
                    f"Total search results: {result_count:,}"
                )
                self.logger.info(f"Found {result_count:,} results")
                print(f"\n{'*' * 60}")
                print(f"SEARCH RESULTS COUNT: {result_count:,}")
                print(f"{'*' * 60}\n")
            else:
                self.report.add_result(
                    "Get search result count",
                    "WARNING",
                    "Could not retrieve accurate result count"
                )
                self.logger.warning("Could not get result count")

            # Step 6: Validate results contain search keyword
            keyword_found = search_page.validate_results_contain_keyword(search_term)

            if keyword_found:
                self.report.add_result(
                    f"Validate results contain '{search_term}'",
                    "PASS",
                    f"Results contain the search keyword '{search_term}'"
                )
                self.logger.info(f"Keyword '{search_term}' found in results")
            else:
                self.report.add_result(
                    f"Validate results contain '{search_term}'",
                    "FAIL",
                    f"Results do not contain keyword '{search_term}'"
                )
                self.logger.warning(f"Keyword '{search_term}' not found in results")

            # Step 7: Apply transmission filter
            transmission_type = self.config["test_data"]["filters"]["transmission"]

            if search_page.filter_by_transmission(transmission_type):
                self.report.add_result(
                    f"Filter by Transmission -> {transmission_type}",
                    "PASS",
                    f"Successfully applied {transmission_type} transmission filter"
                )
                self.logger.info(f"{transmission_type} filter applied")

                # Get filtered results count
                filtered_count = search_page.get_search_result_count()
                if filtered_count > 0:
                    self.logger.info(f"Filtered results count: {filtered_count:,}")
                    print(f"\n{'*' * 60}")
                    print(f"FILTERED RESULTS COUNT ({transmission_type}): {filtered_count:,}")
                    print(f"{'*' * 60}\n")
            else:
                self.report.add_result(
                    f"Filter by Transmission -> {transmission_type}",
                    "WARNING",
                    f"Could not apply {transmission_type} transmission filter"
                )
                self.logger.warning(f"Could not apply {transmission_type} transmission filter")

            # Take final screenshot
            screenshot_path = "screenshots/final_results.png"
            Path("screenshots").mkdir(exist_ok=True)
            page.screenshot(path=screenshot_path)
            self.report.add_result(
                "Take final screenshot",
                "PASS",
                "Final screenshot captured"
            )
            self.logger.info(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            self.logger.error(f"Unexpected error during automation: {str(e)}")
            self.report.add_result(
                "Automation execution",
                "FAIL",
                f"Unexpected error: {str(e)}"
            )
            success = False

        finally:
            # Cleanup
            self.logger.info("\nCleaning up resources")
            if context:
                context.close()
            if browser:
                browser.close()
            if playwright:
                playwright.stop()
            self.logger.info("Resources cleaned up")

            # Generate report
            self.logger.info("\nGenerating test report")
            self.report.generate_report()

            self.logger.info("=" * 80)
            if success:
                self.logger.info("AUTOMATION COMPLETED SUCCESSFULLY")
            else:
                self.logger.warning("AUTOMATION COMPLETED WITH ISSUES")
            self.logger.info("=" * 80)

        return success


def main():
    """Main entry point for the automation framework"""
    try:
        framework = EBayAutomationFramework("config.json")
        success = framework.run_automation()

        print("Check 'reports/test_report.html' for detailed test report")
        print("Check 'logs/test_execution.log' for detailed execution log")
    except Exception as e:
        print(f"Error running automation: {str(e)}")
        raise


if __name__ == "__main__":
    main()
