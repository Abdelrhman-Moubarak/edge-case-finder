import time
from types import SimpleNamespace

import chains as chains

code = '''def divide(dividend, divisor):
    count = 0
    while dividend >= divisor:
        dividend -= divisor
        count += 1
    if (dividend < 0) != (divisor < 0):
        return -count
    return count
'''

description = """Given two integers dividend and divisor, divide two integers without using multiplication, division, and mod operator.

The integer division should truncate toward zero, which means losing its fractional part. For example, 8.345 would be truncated to 8, and -2.7335 would be truncated to -2.

Return the quotient after dividing dividend by divisor.

Note: Assume we are dealing with an environment that could only store integers within the 32-bit signed integer range: [−231, 231 − 1]. For this problem, if the quotient is strictly greater than 231 - 1, then return 231 - 1, and if the quotient is strictly less than -231, then return -231.

 

Example 1:

Input: dividend = 10, divisor = 3
Output: 3
Explanation: 10/3 = 3.33333.. which is truncated to 3.

Example 2:

Input: dividend = 7, divisor = -3
Output: -2
Explanation: 7/-3 = -2.33333.. which is truncated to -2.

 

Constraints:

    -231 <= dividend, divisor <= 231 - 1
    divisor != 0
"""


start = time.perf_counter()
derivation_counter = {"count": 0}


def log(message):
    elapsed = time.perf_counter() - start
    print(f"[{elapsed:7.1f}s] {message}", flush=True)


def with_timing(builder, label):
    def new_builder(*args, **kwargs):
        chain = builder(*args, **kwargs)

        def timed_invoke(inputs):
            if label == "Derivation":
                derivation_counter["count"] += 1
                name = f"Derivation {derivation_counter['count']}"
                log(f"{name}: model started for {inputs['call']}")
            else:
                name = label
                log(f"{name}: started")

            step_start = time.perf_counter()
            try:
                output = chain.invoke(inputs)
            except Exception as error:
                seconds = time.perf_counter() - step_start
                log(f"{name}: FAILED after {seconds:.1f}s, {error}")
                raise

            seconds = time.perf_counter() - step_start
            log(f"{name}: model done in {seconds:.1f}s, {len(output)} characters")
            return output

        return SimpleNamespace(invoke=timed_invoke)

    return new_builder


original_run_derivation = chains.run_derivation


def timed_run_derivation(*args, **kwargs):
    derivation_counter["count"] += 1
    name = f"Derivation {derivation_counter['count']}"
    try:
        value = original_run_derivation(*args, **kwargs)
    except Exception as error:
        log(f"{name}: code FAILED, {error}")
        raise

    log(f"{name}: code ran, value {value}")
    return value


chains.build_generator_chain = with_timing(chains.build_generator_chain, "Generator")
chains.build_reviewer_chain = with_timing(chains.build_reviewer_chain, "Reviewer")
chains.build_reference_chain = with_timing(
    chains.build_reference_chain, "Reference function"
)
chains.run_derivation = timed_run_derivation


start = time.perf_counter()
suite, reference_code, failed_cases = chains.generate_edge_cases(code, description)
total_seconds = time.perf_counter() - start

log(
    f"Finished in {total_seconds:.1f}s: {len(suite.cases)} cases kept, "
    f"{len(failed_cases)} failed"
)

print("\nReference function")
print("=" * 70)
print(reference_code)

print(f"\nGenerated {len(suite.cases)} edge cases\n")
print("=" * 70)

for i, case in enumerate(suite.cases, start=1):
    if case.expected_exception:
        outcome = f"raises {case.expected_exception}"
    else:
        outcome = f"returns {case.expected}"

    print(f"{i}. {case.name}")
    print(f"   call:   {case.call}")
    print(f"   expect: {outcome}")
    print(f"   why:    {case.reason}")
    print("-" * 70)

if failed_cases:
    print(f"\nFailed Cases ({len(failed_cases)})\n")
    print("=" * 70)

    for i, failed in enumerate(failed_cases, start=1):
        print(f"{i}. {failed['call']}")
        print(f"   reason: {failed['reason']}")
        print("-" * 70)