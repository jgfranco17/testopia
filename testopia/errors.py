from typing import Optional


class ExitCode:
    """Class for exit codes."""

    SUCCESS = 0
    RUNTIME_ERROR = 1
    INPUT_ERROR = 2
    TEST_FAILURE = 3


class TestopiaBaseError(Exception):
    """A base Testopia Error class.

    Contains a message, exit_code, and help text show to the user

    exit_code should be a member of ExitCode
    """

    def __init__(self, message: str, exit_code: int, help_text: Optional[str]):
        """Init an STF Error."""
        self.message = message
        self.exit_code = exit_code
        if help_text is None:
            help_text = (
                "Help is available with --help. Use the -v flag to increase output verbosity\n"
                "For more help, check the STF Documentation: "
                "https://docs.arene.com/Vertex/stf/user_manual/overview/"
            )
        self.help_text = help_text
        super().__init__(self.message)


class TestopiaRuntimeError(TestopiaBaseError):
    """General package runtime error class."""

    def __init__(
        self,
        message: str,
        help_text: Optional[str] = None,
    ):
        """Init a custom runtime error."""
        self.message = message
        super().__init__(self.message, ExitCode.RUNTIME_ERROR, help_text)


class TestopiaInputError(TestopiaBaseError):
    """General package input error class."""

    def __init__(
        self,
        message: str,
        help_text: Optional[str] = None,
    ):
        """Init a custom input error."""
        self.message = message
        super().__init__(self.message, ExitCode.INPUT_ERROR, help_text)


class TestopiaTestFailure(TestopiaBaseError):
    """Test failure error class."""

    def __init__(
        self,
        message: str,
        help_text: Optional[str] = None,
    ):
        """Init a test failure error."""
        self.message = message
        super().__init__(self.message, ExitCode.TEST_FAILURE, help_text)
