import re
from dataclasses import dataclass, field
from typing import List

import colorama
from colorama import Fore, Style
from tabulate import tabulate

colorama.init(autoreset=True)


@dataclass
class TestSummary:
    features_passed: int = 0
    features_failed: int = 0
    features_skipped: int = 0
    scenarios_passed: int = 0
    scenarios_failed: int = 0
    scenarios_skipped: int = 0
    steps_passed: int = 0
    steps_failed: int = 0
    steps_skipped: int = 0
    steps_undefined: int = 0
    time_taken: str = ""


@dataclass
class TestReport:
    feature: str = ""
    scenarios: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    summary: TestSummary = field(default_factory=TestSummary)

    def display(self):
        summary_header = "----- Test Summary -----"
        print(f"{summary_header}")
        print(
            f"{Fore.WHITE}Feature:{Style.RESET_ALL} {Fore.WHITE}{self.feature}{Style.RESET_ALL}"
        )
        scenario_names = ", ".join(self.scenarios)
        print(f"{Fore.WHITE}Scenarios:{Style.RESET_ALL} {scenario_names}")
        status_report = {
            "Features": (
                self.summary.features_passed,
                self.summary.features_failed,
                self.summary.features_skipped,
            ),
            "Scenarios": (
                self.summary.scenarios_passed,
                self.summary.scenarios_failed,
                self.summary.scenarios_skipped,
            ),
            "Steps": (
                self.summary.steps_passed,
                self.summary.steps_failed,
                self.summary.steps_skipped,
            ),
        }
        summary_table = []
        for section, data in status_report.items():
            passed, failed, skipped = data
            row = [
                section,
                f"{Fore.GREEN}{passed}{Style.RESET_ALL}",
                f"{Fore.RED}{failed}{Style.RESET_ALL}",
                f"{Fore.YELLOW}{skipped}{Style.RESET_ALL}",
            ]
            summary_table.append(row)

        headers = ["SECTION", "PASSED", "FAILED", "SKIPPED"]
        print(
            tabulate(
                summary_table,
                headers,
                showindex=False,
                tablefmt="outline",
                numalign="center",
            )
        )
        total_failed = [
            self.summary.features_failed,
            self.summary.scenarios_failed,
            self.summary.steps_failed,
        ]
        if sum(total_failed) > 0:
            print(
                f"Found {Fore.LIGHTRED_EX}{self.summary.steps_undefined}{Style.RESET_ALL} failed steps"
            )
        if self.summary.steps_undefined > 0:
            print(
                f"Found {Fore.LIGHTRED_EX}{self.summary.steps_undefined}{Style.RESET_ALL} steps undefined"
            )
        print(f"Time elapsed: {self.summary.time_taken}")
        print("-" * len(summary_header))


class ReportParser:
    def __init__(self, report: str):
        self.report = report
        self.parsed_data = TestReport()

    def parse(self):
        lines = self.report.split("\n")
        for line in lines:
            self._parse_line(line.strip())
        return self.parsed_data

    def _parse_line(self, line):
        if line.startswith("Feature:"):
            self.parsed_data.feature = line[len("Feature:") :].strip()
        elif line.startswith("Scenario:"):
            self.parsed_data.scenarios.append(line[len("Scenario:") :].strip())
        elif (
            line.startswith("Given")
            or line.startswith("When")
            or line.startswith("Then")
        ):
            self.parsed_data.steps.append(line)
        else:
            self._parse_summary(line)

    def _parse_summary(self, line):
        feature_match = re.match(
            r"(\d+) feature(s?) passed, (\d+) failed, (\d+) skipped", line
        )
        scenario_match = re.match(
            r"(\d+) scenario(s?) passed, (\d+) failed, (\d+) skipped", line
        )
        steps_match = re.match(
            r"(\d+) steps? passed, (\d+) failed, (\d+) skipped, (\d+) undefined", line
        )
        time_match = re.match(r"Took (.+)", line)

        if feature_match:
            self.parsed_data.summary.features_passed = int(feature_match.group(1))
            self.parsed_data.summary.features_failed = int(feature_match.group(3))
            self.parsed_data.summary.features_skipped = int(feature_match.group(4))
        elif scenario_match:
            self.parsed_data.summary.scenarios_passed = int(scenario_match.group(1))
            self.parsed_data.summary.scenarios_failed = int(scenario_match.group(3))
            self.parsed_data.summary.scenarios_skipped = int(scenario_match.group(4))
        elif steps_match:
            self.parsed_data.summary.steps_passed = int(steps_match.group(1))
            self.parsed_data.summary.steps_failed = int(steps_match.group(2))
            self.parsed_data.summary.steps_skipped = int(steps_match.group(3))
            self.parsed_data.summary.steps_undefined = int(steps_match.group(4))
        elif time_match:
            self.parsed_data.summary.time_taken = time_match.group(1)
