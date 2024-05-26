import logging
import os
import sys
from io import StringIO
from typing import Any, List, Optional, Type

from behave.configuration import Configuration
from behave.runner import Runner


class TestRunner:
    def __init__(
        self,
        feature_dir: str,
        step_definitions_dir: str,
        export: Optional[bool] = False,
        results_dir: Optional[str] = "results",
        log_level: Optional[int] = logging.INFO,
    ) -> None:
        """
        Initialize the TestRunner with directories for features, step definitions, and results.

        :param feature_dir: Directory containing feature files.
        :param step_definitions_dir: Directory containing step definitions.
        :param results_dir: Directory to save test results.
        :param log_level: Logging level (default: logging.INFO).
        """
        self.feature_dir = feature_dir
        self.step_definitions_dir = step_definitions_dir
        self.export = export
        self.results_dir = results_dir
        self._old_stdout: Optional[StringIO] = None
        self._mystdout: Optional[StringIO] = None
        self.results: str = ""
        self.logger = self.__setup_logger(log_level)

        # Ensure results directory exists
        if export:
            if not os.path.exists(self.results_dir):
                os.makedirs(self.results_dir)
                self.logger.info(f"Created results directory: {self.results_dir}")

    def __setup_logger(self, level: int) -> logging.Logger:
        """
        Set up the logger for the TestRunner.

        :param log_level: Logging level.
        :return: Configured logger.
        """
        logger = logging.getLogger("TestRunner")
        logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def __enter__(self) -> "TestRunner":
        """
        Enter the runtime context related to this object.
        :return: self
        """
        # Redirect stdout to capture Behave output
        self.logger.info("Entering TestRunner context")
        self._old_stdout = sys.stdout
        sys.stdout = self._mystdout = StringIO()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """
        Exit the runtime context related to this object.
        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Traceback object
        :return: True if exception is handled, None otherwise
        """
        sys.stdout = self._old_stdout
        if self._mystdout:
            self.results = self._mystdout.getvalue()

        # Optionally save results to file
        results_file = os.path.join(self.results_dir, "results.txt")
        with open(results_file, "w") as file:
            file.write(self.results)
        self.logger.info(f"Results written to {results_file}")

        if exc_type:
            self.logger.error(
                "Exception occurred", exc_info=(exc_type, exc_val, exc_tb)
            )

        self.logger.info("Exiting TestRunner context")

    def run(self, tags: Optional[str] = None, format: Optional[str] = "pretty") -> str:
        """
        Run the Behave tests.

        :param tags: Tags to filter which tests to run.
        :param format: Format of the test results (e.g., "pretty", "json").
        :return: Results of the Behave test run as a string.
        """
        self.logger.info(f"Output format: {format}")
        if tags:
            all_tags = ", ".join(tags)
            self.logger.info(f"Targeting {len(tags)} tags: {all_tags}")
        else:
            self.logger.info("No tags selected, running full suite")

        config = Configuration()
        config.paths = [self.feature_dir]
        config.tags = tags if tags else []
        config.format = [format]
        config.stdout_capture = False
        config.stderr_capture = False
        config.log_capture = False

        try:
            runner = Runner(config)
            runner.run()
        except Exception as e:
            self.logger.error(f"Error running Behave: {e}")
            return f"Error running Behave: {e}"

        self.logger.info("Behave tests completed")
        return self._mystdout.getvalue() if self._mystdout else ""

    def get_results(self) -> str:
        """
        Retrieve the results of the last test run.

        :return: Contents of the results as a string.
        """
        self.logger.info("Retrieving test results")
        return self.results
