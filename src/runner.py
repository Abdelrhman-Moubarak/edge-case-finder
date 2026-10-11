import ast
import os
import re
import subprocess
import sys
import tempfile


RESULT_MARKER = "@@RESULT@@"


class RunnerError(Exception):
    pass


def extract_code(text: str) -> str:
    blocks = re.findall(r"```(?:python)?[ \t]*\n(.*?)```", text, re.DOTALL)
    if blocks:
        return blocks[0].strip()
    return text.strip()


def run_python(code: str, timeout: int = 10) -> dict[str, str | int | bool]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "snippet.py")
        with open(path, "w", encoding="utf-8") as file:
            file.write(code)

        try:
            completed = subprocess.run(
                [sys.executable, path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": "", "returncode": -1, "timed_out": True}

    return {
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "returncode": completed.returncode,
        "timed_out": False,
    }


def run_derivation(code: str, timeout: int = 10) -> str:
    full_code = code + "\n" + f'print("{RESULT_MARKER}", repr(result))\n'
    output = run_python(full_code, timeout)

    if output["timed_out"]:
        raise RunnerError(f"Derivation code ran longer than {timeout} seconds")

    if output["returncode"] != 0:
        error_lines = str(output["stderr"]).strip().splitlines()
        last_line = error_lines[-1] if error_lines else "unknown error"
        raise RunnerError(f"Derivation code crashed: {last_line}")

    value_text = None
    for line in reversed(str(output["stdout"]).splitlines()):
        if line.startswith(RESULT_MARKER):
            value_text = line[len(RESULT_MARKER):].strip()
            break

    if value_text is None:
        raise RunnerError("Derivation code did not print a result")

    try:
        ast.literal_eval(value_text)
    except (ValueError, SyntaxError):
        raise RunnerError(f"Derived value is not a plain literal: {value_text}")

    return value_text