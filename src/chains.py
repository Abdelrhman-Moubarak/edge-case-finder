import ast

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import PydanticOutputParser


from models.edge_case import EdgeCase, EdgeCaseSuite, check_suite_ready, is_filled
from models.prompts import EDGE_CASE_GENERATOR_PROMPT, EDGE_CASE_REVIEWER_PROMPT, REFERENCE_FUNCTION_PROMPT, FIX_PROMPT
from src.llm_client import QwenLLM
from src.runner import RunnerError, extract_code, run_derivation


parser = PydanticOutputParser(pydantic_object=EdgeCaseSuite)


def build_generator_chain(llm=None):
    llm = llm or QwenLLM()

    prompt = EDGE_CASE_GENERATOR_PROMPT.partial(
        format_instructions=parser.get_format_instructions()
    )

    return prompt | llm


def build_reviewer_chain(llm=None):
    llm = llm or QwenLLM()

    prompt = EDGE_CASE_REVIEWER_PROMPT.partial(
        format_instructions=parser.get_format_instructions()
    )

    return prompt | llm


def build_reference_chain(llm=None):
    llm = llm or QwenLLM()

    return REFERENCE_FUNCTION_PROMPT | llm


def get_function_signature(function_code: str) -> str:
    tree = ast.parse(function_code)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            signature = f"def {node.name}({ast.unparse(node.args)})"
            if node.returns is not None:
                signature += f" -> {ast.unparse(node.returns)}"
            return signature + ":"

    raise ValueError("No function definition found in the submitted code")


def needs_derivation(case: EdgeCase) -> bool:
    return not is_filled(case.expected_exception)


def generate_edge_cases(function_code: str, description: str) -> tuple[EdgeCaseSuite, str, list[dict[str, str]]]:
    
    generator_raw = build_generator_chain().invoke(
        {
            "function_code": function_code,
            "description": description,
        }
    )
    try:
        generator_suite = parser.parse(generator_raw)
    except OutputParserException:
        raise

    
    reviewer_raw = build_reviewer_chain().invoke(
        {
            "function_code": function_code,
            "description": description,
            "candidate_cases": generator_suite.model_dump_json(),
        }
    )
    try:
        suite = parser.parse(reviewer_raw)
    except OutputParserException:
        raise

    
    for case in suite.cases:
        case.expected = None

    
    function_signature = get_function_signature(function_code)
    reference_raw = build_reference_chain().invoke(
        {
            "description": description,
            "function_signature": function_signature,
        }
    )
    reference_code = extract_code(reference_raw)
    if reference_code == "":
        raise RunnerError("The model returned no reference function")


    kept_cases = []
    failed_cases = []

    for case in suite.cases:
        if not needs_derivation(case):
            kept_cases.append(case)
            continue

        try:
            case.expected = run_derivation(
                reference_code + "\n\nresult = " + case.call
            )
        except RunnerError as error:
            failed_cases.append({"call": case.call, "reason": str(error)})
            continue

        kept_cases.append(case)

    suite.cases = kept_cases
    check_suite_ready(suite)

    return suite, reference_code, failed_cases