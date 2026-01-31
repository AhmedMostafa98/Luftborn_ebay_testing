import logging
from pathlib import Path
from datetime import datetime
import pytest
from html import escape
from logger_report import TestLogger, TestReport

# try to import pytest-html builder
try:
    from py.xml import html
except Exception:
    html = None

# module-level holder for generated session html log and TestReport instance
GENERATED_SESSION_HTML = None
TEST_REPORT = None

@pytest.fixture(scope="session", autouse=True)
def logger(request):
    """Configure session logger via logger_report and create a TestReport for results."""
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_name = f"test_{timestamp}.log"
    log_path = logs_dir / log_name
    request.config.ebay_log_file = str(log_path)

    # Use TestLogger to set up handlers consistently for this project
    logger = TestLogger.setup_logger(log_file=log_name, log_level="DEBUG")
    logger.info("=== TEST SESSION START: %s ===", timestamp)

    # create TestReport instance to be used during the session
    global TEST_REPORT
    TEST_REPORT = TestReport(report_file=f"{log_path.stem}.html")
    request.config.ebay_test_report = TEST_REPORT

    yield logger

    logger.info("=== TEST SESSION END ===")

    # finalize TestReport -> generate HTML report
    global GENERATED_SESSION_HTML
    try:
        if TEST_REPORT:
            TEST_REPORT.generate_report()
            if TEST_REPORT.report_path.exists():
                GENERATED_SESSION_HTML = str(TEST_REPORT.report_path)
                request.config.ebay_log_html = GENERATED_SESSION_HTML
                logger.info("Generated HTML session report: %s", GENERATED_SESSION_HTML)
            else:
                request.config.ebay_log_html = None
    except Exception as exc:
        logger.exception("Failed to generate session HTML report: %s", exc)
        request.config.ebay_log_html = None

    # flush and (TestLogger.setup_logger) already manages handlers; ensure flush
    for h in logger.handlers[:]:
        try:
            h.flush()
            h.close()
        except Exception:
            pass
        logger.removeHandler(h)
    logging.shutdown()


@pytest.fixture(autouse=True)
def per_test_logging(logger, request):
    """Log start/end of each test and flush handlers so log file is populated immediately."""
    logger.info(">>> START TEST: %s", request.node.name)
    for h in logger.handlers:
        try:
            h.flush()
        except Exception:
            pass
    yield
    logger.info("<<< END TEST: %s", request.node.name)
    for h in logger.handlers:
        try:
            h.flush()
        except Exception:
            pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach screenshot and session log to report for both pass and fail (on 'call')."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = item.name
    suffix = report.outcome  # "passed" or "failed"
    screenshot_file = screenshots_dir / f"{name}_{suffix}_{timestamp}.png"

    logger = item.funcargs.get("logger", logging.getLogger("ebay_tests"))

    # Prefer pytest-playwright 'page', else context->pages[0], else browser->contexts()[0].pages[0]
    page = item.funcargs.get("page")
    context = item.funcargs.get("context")
    browser = item.funcargs.get("browser")

    try:
        target = None
        if page is not None:
            target = page
        elif context is not None:
            pages = getattr(context, "pages", None)
            if pages:
                target = pages[0]
        elif browser is not None:
            try:
                contexts = getattr(browser, "contexts", None)
                if callable(contexts):
                    contexts = contexts()
                if contexts:
                    pages = getattr(contexts[0], "pages", None)
                    if pages:
                        target = pages[0]
            except Exception:
                target = None

        if target and hasattr(target, "screenshot"):
            try:
                # sync API: page.screenshot(path=...)
                target.screenshot(path=str(screenshot_file))
                logger.info("Captured screenshot for %s: %s", report.outcome, screenshot_file)
            except Exception as e:
                logger.exception("Failed to capture screenshot: %s", e)
        else:
            logger.debug("No page/context/browser available to capture screenshot for %s", report.outcome)
    except Exception as e:
        logger.exception("Error while attempting screenshot capture: %s", e)

    # Ensure logs are flushed before attaching
    try:
        for h in logger.handlers:
            try:
                h.flush()
            except Exception:
                pass
    except Exception:
        pass

    # Attach screenshot and session log contents to pytest-html report extras (if plugin present)
    try:
        from pytest_html import extras

        extra = getattr(report, "extra", [])

        if screenshot_file.exists():
            extra.append(extras.image(str(screenshot_file), mime_type="image/png"))

        log_path = getattr(item.config, "ebay_log_file", None)
        if log_path and Path(log_path).exists():
            raw = Path(log_path).read_text(encoding="utf-8")
            max_len = 10000
            if len(raw) > max_len:
                raw = "...(truncated)...\n" + raw[-max_len:]
            extra.append(extras.text(raw, name="session_log"))

        # record per-test result into TestReport (for the custom HTML report)
        try:
            if TEST_REPORT:
                status = "PASS" if report.outcome == "passed" else "FAIL" if report.outcome == "failed" else report.outcome.upper()
                message = ""
                try:
                    # prefer the longrepr text on failures
                    message = report.longreprtext if report.failed else ""
                except Exception:
                    message = ""
                screenshot_value = str(screenshot_file) if screenshot_file.exists() else ""
                TEST_REPORT.add_result(test_name=item.nodeid, status=status, message=message, screenshot=screenshot_value)
        except Exception:
            pass

        report.extra = extra
    except Exception:
        # pytest-html not installed or other error — ignore
        pass


# =============================================================================
# pytest-html hooks: ensure header, rows, and per-row HTML content render properly
# =============================================================================

def pytest_html_results_table_header(cells):
    """Ensure table has expected headers so table is not empty."""
    if html is None:
        return
    # clear/normalize and set our columns: Result | Test | Duration | Links
    try:
        # insert at beginning for known ordering (some pytest-html versions pre-populate differently)
        cells.insert(0, html.th("Result"))
        cells.insert(1, html.th("Test"))
        cells.insert(2, html.th("Duration"))
        cells.append(html.th("Links"))
    except Exception:
        pass


def pytest_html_results_table_row(report, cells):
    """Populate the table row with result, nodeid and duration."""
    if html is None:
        return
    try:
        # prefer to set values at fixed positions for consistency
        # First cell: outcome
        cells.insert(0, html.td(report.outcome))
        # Second cell: nodeid
        cells.insert(1, html.td(report.nodeid))
        # Third cell: duration if available (rounded)
        dur = getattr(report, "duration", None)
        dur_text = f"{dur:.2f}s" if isinstance(dur, (float, int)) else ""
        cells.insert(2, html.td(dur_text))
    except Exception:
        pass


def pytest_html_results_table_html(report, data):
    """Render images and session log (and link to generated HTML session log) in the Links column."""
    if html is None:
        return
    try:
        if not getattr(report, "extra", None) and not GENERATED_SESSION_HTML:
            return

        cont = html.div()
        # link to generated session HTML log if available
        if GENERATED_SESSION_HTML and Path(GENERATED_SESSION_HTML).exists():
            cont.append(html.div(html.a("Session log (HTML)", href=Path(GENERATED_SESSION_HTML).as_posix(), target="_blank")))

        for e in getattr(report, "extra", []) or []:
            if getattr(e, "get", None):
                mime = e.get("mime_type", "") or ""
                name = e.get("name", "")
                content = e.get("content", "")
                if mime.startswith("image"):
                    cont.append(html.div(html.img(src=content, style="max-width:240px;margin:4px 0;")))
                elif name == "session_log" or e.get("type") == "text":
                    text = escape(content if isinstance(content, str) else str(content))
                    cont.append(html.details(html.summary("session_log"), html.pre(text)))
            else:
                try:
                    cont.append(html.div(str(e)))
                except Exception:
                    pass

        if cont.children:
            data.append(html.td(cont))
    except Exception:
        pass


def pytest_html_results_summary(prefix, summary, postfix):
    """Add link to generated session HTML log to summary if available."""
    if html is None:
        return
    try:
        if GENERATED_SESSION_HTML and Path(GENERATED_SESSION_HTML).exists():
            prefix.append(html.p(html.a("Session Log (HTML)", href=Path(GENERATED_SESSION_HTML).as_posix(), target="_blank")))
    except Exception:
        pass
