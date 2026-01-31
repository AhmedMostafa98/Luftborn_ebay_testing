"""
Logging and Reporting module for test execution
Provides test logger and HTML report generation
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class TestLogger:
    """Configure and manage logging for test execution"""

    @staticmethod
    def setup_logger(log_file: str = "test_execution.log", log_level: str = "INFO") -> logging.Logger:
        """
        Setup logger for test execution

        Args:
            log_file (str): Path to log file
            log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Returns:
            logging.Logger: Configured logger instance
        """
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        log_path = logs_dir / log_file

        # Configure logging
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, log_level.upper()))

        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # File handler
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(getattr(logging, log_level.upper()))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logger.info(f"Logging initialized - Log file: {log_path}")
        return logger


class TestReport:
    """Generate HTML test execution report"""

    def __init__(self, report_file: str = "test_report.html"):
        """
        Initialize report generator

        Args:
            report_file (str): Path to HTML report file
        """
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        self.report_path = reports_dir / report_file
        self.test_results = []
        self.start_time = datetime.now()

    def add_result(self, test_name: str, status: str, message: str = "", screenshot: str = "") -> None:
        """
        Add test result to report

        Args:
            test_name (str): Name of the test step
            status (str): Status (PASS, FAIL, WARNING)
            message (str): Result message
            screenshot (str): Path to screenshot
        """
        result = {
            "name": test_name,
            "status": status,
            "message": message,
            "screenshot": screenshot,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)

    def generate_report(self) -> None:
        """Generate HTML report from collected results"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARNING"])

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Execution Report</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #333;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .summary {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .summary-box {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            min-width: 150px;
        }}
        .summary-label {{
            font-weight: bold;
            color: #666;
            font-size: 0.9em;
        }}
        .summary-value {{
            font-size: 1.8em;
            font-weight: bold;
            margin-top: 5px;
        }}
        .pass {{ color: #28a745; }}
        .fail {{ color: #dc3545; }}
        .warning {{ color: #ffc107; }}
        .results {{
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .result-item {{
            border-bottom: 1px solid #eee;
            padding: 15px;
            display: flex;
            align-items: flex-start;
            gap: 15px;
        }}
        .result-item:last-child {{
            border-bottom: none;
        }}
        .status-badge {{
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
            color: white;
            min-width: 60px;
            text-align: center;
        }}
        .status-badge.pass {{
            background-color: #28a745;
        }}
        .status-badge.fail {{
            background-color: #dc3545;
        }}
        .status-badge.warning {{
            background-color: #ffc107;
            color: black;
        }}
        .result-content {{
            flex-grow: 1;
        }}
        .result-name {{
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }}
        .result-message {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        .result-timestamp {{
            color: #999;
            font-size: 0.8em;
        }}
        .screenshot-link {{
            color: #007bff;
            text-decoration: none;
            font-size: 0.9em;
            margin-top: 5px;
            display: inline-block;
        }}
        .screenshot-link:hover {{
            text-decoration: underline;
        }}
        .footer {{
            margin-top: 20px;
            padding: 15px;
            background-color: white;
            border-radius: 5px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Execution Report</h1>
        <p>eBay Automation Framework - Mazda MX-5 Search & Filter Test</p>
    </div>

    <div class="summary">
        <div class="summary-box">
            <div class="summary-label">Total Tests</div>
            <div class="summary-value">{total_tests}</div>
        </div>
        <div class="summary-box">
            <div class="summary-label">Passed</div>
            <div class="summary-value pass">{passed_tests}</div>
        </div>
        <div class="summary-box">
            <div class="summary-label">Failed</div>
            <div class="summary-value fail">{failed_tests}</div>
        </div>
        <div class="summary-box">
            <div class="summary-label">Warnings</div>
            <div class="summary-value warning">{warning_tests}</div>
        </div>
        <div class="summary-box">
            <div class="summary-label">Duration</div>
            <div class="summary-value">{duration:.2f}s</div>
        </div>
    </div>

    <div class="results">
"""

        for result in self.test_results:
            status_lower = result["status"].lower()
            html_content += f"""
        <div class="result-item">
            <div class="status-badge {status_lower}">{result['status']}</div>
            <div class="result-content">
                <div class="result-name">{result['name']}</div>
                <div class="result-message">{result['message']}</div>
                <div class="result-timestamp">{result['timestamp']}</div>
"""
            if result["screenshot"]:
                html_content += f'                <a href="{result["screenshot"]}" class="screenshot-link">View Screenshot</a>\n'

            html_content += """            </div>
        </div>
"""

        html_content += f"""
    </div>

    <div class="footer">
        <p>Report generated on {end_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total Duration: {duration:.2f} seconds</p>
    </div>
</body>
</html>
""".format(end_time=end_time, duration=duration)

        with open(self.report_path, 'w') as f:
            f.write(html_content)

        logging.info(f"Report generated: {self.report_path}")
