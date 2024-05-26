import re
from dataclasses import dataclass, field
from typing import List

import colorama
from colorama import Fore, Style

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
    scenario: str = ""
    steps: List[str] = field(default_factory=list)
    summary: TestSummary = field(default_factory=TestSummary)

    def display(self):
        summary_header = "----- Test Summary -----"
        print(f"\n{summary_header}")
        print(
            f"{Fore.WHITE}Feature:{Style.RESET_ALL} {Fore.WHITE}{self.feature}{Style.RESET_ALL}"
        )
        print(f"{Fore.WHITE}Scenario:{Style.RESET_ALL} {self.scenario}")
        print(f"Ran {Fore.CYAN}{len(self.steps)}{Style.RESET_ALL} steps")
        print(
            f"{Fore.GREEN}{self.summary.features_passed} feature(s) passed,{Style.RESET_ALL} {Fore.RED}{self.summary.features_failed} failed,{Style.RESET_ALL} {Fore.YELLOW}{self.summary.features_skipped} skipped{Style.RESET_ALL}"
        )
        print(
            f"{Fore.GREEN}{self.summary.scenarios_passed} scenario(s) passed,{Style.RESET_ALL} {Fore.RED}{self.summary.scenarios_failed} failed,{Style.RESET_ALL} {Fore.YELLOW}{self.summary.scenarios_skipped} skipped{Style.RESET_ALL}"
        )
        print(
            f"{Fore.GREEN}{self.summary.steps_passed} step(s) passed,{Style.RESET_ALL} {Fore.RED}{self.summary.steps_failed} failed,{Style.RESET_ALL} {Fore.YELLOW}{self.summary.steps_skipped} skipped,{Style.RESET_ALL} {Fore.LIGHTRED_EX}{self.summary.steps_undefined} undefined{Style.RESET_ALL}"
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
            self.parsed_data.scenario = line[len("Scenario:") :].strip()
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
