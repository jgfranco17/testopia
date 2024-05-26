from testopia.runner import TestRunner


def main():
    runner = TestRunner(feature_dir="features", step_definitions_dir="steps")
    with TestRunner(feature_dir="features", step_definitions_dir="steps") as runner:
        try:
            results = runner.run(tags="@smoke", format="pretty")
            print(results)
        except Exception as e:
            print(f"Exception during test run: {e}")
