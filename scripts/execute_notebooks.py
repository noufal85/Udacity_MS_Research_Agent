"""Execute and save both deliverables using this environment's Python kernel."""

import sys
from pathlib import Path

import nbformat
from jupyter_client import KernelManager
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT / 'project' / 'starter'
sys.path.insert(0, str(STARTER))
sys.path.insert(0, str(ROOT))

from lib.udaplay import configure_environment
from scripts.verify_submission import NAMES, verify


def execute_notebook(notebook, directory):
    manager = KernelManager(kernel_name='python3')
    manager.kernel_spec.argv = [
        sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}',
    ]
    client = NotebookClient(
        notebook, km=manager, timeout=180,
        resources={'metadata': {'path': str(directory)}},
    )
    # KernelManager is supplied explicitly, so this runner owns its cleanup.
    try:
        with client.setup_kernel(cwd=str(directory)):
            client.execute()
    finally:
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)
        if client.kc:
            client.kc.stop_channels()
    return notebook


def main():
    configure_environment()
    # Validate configuration before executing either notebook or starting paid requests.
    for name in NAMES:
        path = STARTER / name
        notebook = nbformat.read(path, as_version=4)
        execute_notebook(notebook, STARTER)
        nbformat.write(notebook, path)
        print(f'Executed and saved {name}', flush=True)
    problems = verify()
    if problems:
        raise RuntimeError('\n'.join(problems))
    print('Both deliverables pass the saved-execution gate.')


if __name__ == '__main__':
    main()
