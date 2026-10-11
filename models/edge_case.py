from pydantic import BaseModel, Field


class EdgeCase(BaseModel):
    name: str = Field(
        description="Short snake_case name for the test, e.g. empty_list."
    )
    call: str = Field(
        description="One Python expression that calls the function with the test input, e.g. average([1, 2, 3])."
    )
    expected: str | None = Field(
        default=None,
        description="Always null. A later step computes it by running code.",
    )
    expected_exception: str | None = Field(
        default=None,
        description="Exception class name if the call should raise, e.g. ValueError. Null otherwise.",
    )
    reason: str = Field(
        description="One or two sentences: why this input is tricky and which rule of the description it targets. No arithmetic and no computed results."
    )


class EdgeCaseSuite(BaseModel):
    cases: list[EdgeCase] = Field(min_length=1, max_length=10)


def is_filled(value: str | None) -> bool:
    return value is not None and value.strip() != ""


def get_filled_outcomes(case: EdgeCase) -> list[str]:
    outcomes: dict[str, str | None] = {
        "expected": case.expected,
        "expected_exception": case.expected_exception,
    }

    filled: list[str] = []
    for field_name, value in outcomes.items():
        if is_filled(value):
            filled.append(field_name)
    return filled


def check_suite_ready(suite: EdgeCaseSuite) -> None:
    for case in suite.cases:
        if len(get_filled_outcomes(case)) == 0:
            raise ValueError(
                f"Case '{case.name}' still has no expected or expected_exception"
            )