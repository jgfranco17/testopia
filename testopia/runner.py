import logging
import os
import sys
from io import StringIO
from typing import Any, List, Optional, Type

from behave.configuration import Configuration
from behave.runner import Runner

from .errors import TestopiaInputError, TestopiaRuntimeError
from .parser import ReportParser


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
        self.results_file = os.path.join(self.results_dir, "report.txt")
        self._old_stdout: Optional[StringIO] = None
        self._my_stdout: Optional[StringIO] = None
        self.results: str = ""
        self.logger = self.__setup_logger(log_level)
        self.output = ""

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
        log_format = "[%(asctime)s][%(levelname)s] %(message)s"
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
        self._old_stdout = sys.stdout
        sys.stdout = self._my_stdout = StringIO()
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
        if self._my_stdout:
            self.results = self._my_stdout.getvalue()

        # Optionally save results to file
        if self.export:
            with open(self.results_file, "w") as file:
                file.write(self.results)
            self.logger.debug(f"Results written to {self.results_file}")

        if exc_type:
            self.logger.error(
                "Exception occurred", exc_info=(exc_type, exc_val, exc_tb)
            )

        self.logger.debug("Test runs complete, closing runner")
        return None

    def __validate_tags(self, tags: List[str]) -> str:
        self.logger.debug(f"Found {len(tags)} tags")
        valid_tags = []
        if not tags:
            return None
        for tag in tags:
            fixed_tag = tag

            if not tag.startswith("@"):
                fixed_tag = f"@{tag}"
            if fixed_tag in valid_tags:
                raise TestopiaInputError(f"Duplicate tag {fixed_tag} found in tags")

            valid_tags.append(fixed_tag)

        all_tags = " ".join(valid_tags)
        self.logger.debug(f"Running {len(valid_tags)} tag(s): {all_tags}")
        return all_tags

    def run(
        self, tags: Optional[List[str]] = None, format: Optional[str] = "pretty"
    ) -> str:
        """
        Run the Behave tests.

        :param tags: Tags to filter which tests to run.
        :param format: Format of the test results (e.g., "pretty", "json").
        :return: Results of the Behave test run as a string.
        """
        self.logger.debug(f"Output format: {format}")

        # Parse and validate tags
        if tags:
            validated_tags = self.__validate_tags(tags)
        else:
            self.logger.debug("No tags selected, running full suite")

        # Declare if exported or not
        if self.export:
            self.logger.debug(f"Results will be exported: {self.results_dir}")

        config = Configuration()
        config.paths = [self.feature_dir]
        config.format = [format]
        config.tags.check(validated_tags)
        config.stdout_capture = False
        config.stderr_capture = False
        config.log_capture = False

        try:
            runner = Runner(config)
            runner.run()
        except Exception as e:
            self.logger.error(f"Error running Behave: {e}")
            raise TestopiaRuntimeError(f"Test execution failed: {e}") from e

        self.logger.debug("Gherkin tests completed")
        sys.stdout = self._old_stdout
        return self._my_stdout.getvalue()

    def display_results(self) -> str:
        """
        Retrieve the results of the last test run.

        :return: Contents of the results as a string.
        """
        if self.results:
            self.logger.debug("Retrieving test results")
            report = ReportParser(self.results).parse()
            report.display()

        else:
            print("No results to show.")
