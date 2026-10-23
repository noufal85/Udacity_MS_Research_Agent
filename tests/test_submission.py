import importlib.util
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]


def test_submission_verifier_exists():
    assert (ROOT / 'scripts' / 'verify_submission.py').is_file()


def verifier():
    spec = importlib.util.spec_from_file_location('verifier', ROOT / 'scripts' / 'verify_submission.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_unexecuted_notebook_cannot_pass_readiness():
    notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell('print(1)')])
    problems = verifier().execution_problems(notebook)
    assert any('unexecuted' in problem for problem in problems)


def test_error_output_cannot_pass_readiness():
    cell = nbformat.v4.new_code_cell('raise RuntimeError()', execution_count=1)
    cell.outputs = [nbformat.v4.new_output('error', ename='RuntimeError', evalue='failure', traceback=[])]
    problems = verifier().execution_problems(nbformat.v4.new_notebook(cells=[cell]))
    assert any('error' in problem for problem in problems)


def test_printed_text_without_execution_counts_cannot_pass_readiness():
    cell = nbformat.v4.new_code_cell('print(1)')
    cell.outputs = [nbformat.v4.new_output('stream', name='stdout', text='1')]
    problems = verifier().execution_problems(nbformat.v4.new_notebook(cells=[cell]))
    assert any('unexecuted' in problem for problem in problems)


def test_runner_executes_real_kernel_with_expected_directory(tmp_path):
    import sys
    sys.path.insert(0, str(ROOT))
    from scripts.execute_notebooks import execute_notebook

    notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(
        'from pathlib import Path\nprint(Path.cwd())\nprint(2 + 2)'
    )])
    executed = execute_notebook(notebook, tmp_path)
    assert executed.cells[0].execution_count == 1
    text = ''.join(output.get('text', '') for output in executed.cells[0].outputs)
    assert str(tmp_path.resolve()) in text
    assert '4' in text
