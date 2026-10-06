from langchain_core.prompts import PromptTemplate

EDGE_CASE_PROMPT = PromptTemplate.from_template(
    """You are a software testing expert.

Below is a Python function and a description of what it should do.
Propose edge cases that are likely to expose bugs in it.

Function:
{function_code}

Description:
{description}

Rules:
1. Propose between 5 and 10 edge cases.
2. Cover different kinds: empty or minimal inputs, boundary values, zero and negatives, unusual types, very large inputs, duplicates.
3. The expected result must come ONLY from the description, NEVER from what the code currently does.
4. If the description says an input should raise an error, set expected_exception to the exception class name and leave expected as null.
5. Inputs must be JSON values: numbers, strings, booleans, null, lists, objects.
6. Do not repeat the same edge case.
7. "reason" must be one short sentence.

{format_instructions}
"""
)