from testopia.runner import TestRunner


def main():
    runner = TestRunner(
        feature_dir="./sample/features",
        step_definitions_dir="./sample/steps",
        export=True,
    )
    results = None
    with runner:
        results = runner.run(format="pretty", tags=["@smoke"])

    print("Gathered results from runner:")
    print(results)


if __name__ == "__main__":
    main()
