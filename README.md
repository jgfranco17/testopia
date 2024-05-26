# Behave Runner

Behave Runner is a Python package that wraps Behave for running tests programmatically.
It allows you to run Behave tests from within a Python script, capture the results, and
handle exceptions cleanly.

## Installation

Install the package using Poetry:

```shell
poetry add behave-runner
```

## Usage

```python
from testopia.runner import TestRunner

with TestRunner(feature_dir="features", step_definitions_dir="steps") as runner:
    results = runner.run(tags=["@smoke", "@regression"], format="pretty")
    print(results)
```
