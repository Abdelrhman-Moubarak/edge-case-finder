## Test for the Models/* files (PASSED)

# from models.edge_case import EdgeCaseSuite
# from models.prompts import EDGE_CASE_PROMPT

# sample = {"cases": [{"name": "empty_list", "args": [[]], "expected": None,
#                      "expected_exception": "ValueError", "reason": "No elements to average."}]}

# print(EdgeCaseSuite.model_validate(sample))

# print(EDGE_CASE_PROMPT.format(
#     function_code = "def average(xs): return sum(xs) / len(xs)",
#     description = "Returns the mean of a list of numbers.",
#     format_instructions = "(filled in step 2)",
# ))


## Test for the src/llm_client file (PASSED)

# from src.llm_client import QwenLLM

# llm = QwenLLM()
# print(llm.invoke("Say hello in one short sentence."))