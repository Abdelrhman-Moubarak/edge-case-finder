from typing import Any

from pydantic import BaseModel, Field


class EdgeCase(BaseModel):
    name: str = Field(
        description="Short snake_case name for the test, e.g. empty_list."
    )
    args: list[Any] = Field(
        description="Positional arguments to call the function with, as JSON values."
    )
    expected: Any = Field(
        default=None,
        description="The expected return value according to the description.",
    )
    expected_exception: str | None = Field(
        default=None,
        description="Exception class name if the function should raise, e.g. ValueError.",
    )
    reason: str = Field(
        description="One short sentence on why this input is tricky."
    )


class EdgeCaseSuite(BaseModel):
    cases: list[EdgeCase] = Field(min_length=1, max_length=10)