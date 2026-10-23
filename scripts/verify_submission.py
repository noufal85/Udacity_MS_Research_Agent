"""Check notebook source or enforce the Udacity saved-execution gate."""

import argparse
import json
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT / 'project' / 'starter'
NAMES = ('Udaplay_01_starter_project.ipynb', 'Udaplay_02_starter_project.ipynb')


def execution_problems(notebook):
    problems = []
    cells = [cell for cell in notebook.cells if cell.cell_type == 'code' and cell.source.strip()]
    if not cells:
        problems.append('Notebook has no code cells')
    for index, cell in enumerate(cells, start=1):
        if cell.execution_count is None:
            problems.append(f'Code cell {index} is unexecuted')
        if any(output.output_type == 'error' for output in cell.get('outputs', [])):
            problems.append(f'Code cell {index} contains an error output')
    if not any(cell.get('outputs') for cell in cells):
        problems.append('Notebook has no saved outputs')
    return problems


def verify(source_only=False):
    problems = []
    for name in NAMES:
        notebook = nbformat.read(STARTER / name, as_version=4)
        nbformat.validate(notebook)
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type == 'code':
                compile(cell.source, f'{name}:cell-{index}', 'exec')
                if 'TODO' in cell.source:
                    problems.append(f'{name}: unfinished TODO in code cell {index}')
        if not source_only:
            problems.extend(f'{name}: {problem}' for problem in execution_problems(notebook))
            output_text = json.dumps([cell.get('outputs', []) for cell in notebook.cells], ensure_ascii=False)
            required = ('Validated game records:', 'Collection', 'Grand Theft Auto') if name == NAMES[0] else (
                'Pokémon Gold and Silver', 'Mortal Kombat X',
                'retrieve_game', 'evaluate_retrieval', 'game_web_search',
                'Required local, fallback, trace and citation demonstrations passed.',
            )
            for marker in required:
                if marker not in output_text:
                    problems.append(f'{name}: missing runtime evidence marker {marker!r}')
    if len(list((STARTER / 'games').glob('*.json'))) != 15:
        problems.append('Expected exactly 15 supplied game JSON files')
    if not (STARTER / 'lib' / 'state_machine.py').is_file():
        problems.append('Supplied lib/ state machine is missing')
    return problems


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-only', action='store_true', help='Check source, not execution evidence')
    args = parser.parse_args()
    problems = verify(args.source_only)
    for problem in problems:
        print('FAIL:', problem)
    if problems:
        raise SystemExit(1)
    print('PASS:', 'source validation' if args.source_only else 'saved notebook execution and required evidence')
