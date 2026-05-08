#!/usr/bin/env python3
import sys
from pathlib import Path
import nbformat

def check_notebook(nb_path: Path) -> bool:
    nb = nbformat.read(nb_path, as_version=nbformat.NO_CONVERT)
    for i, cell in enumerate(nb.cells):
        if cell.get("cell_type") == "code":
            if cell.get("outputs"):
                print(f"Outputs found in {nb_path} at cell {i}")
                return False
            if cell.get("execution_count") is not None:
                print(f"Execution count found in {nb_path} at cell {i}")
                return False
    return True

def main() -> int:
    root = Path('.')
    failed = False
    for path in root.rglob('*.ipynb'):
        if '.ipynb_checkpoints' in path.parts:
            continue
        ok = check_notebook(path)
        if not ok:
            failed = True
    if failed:
        print('\nOne or more notebooks contain outputs or execution counts. Run `nbstripout` or `jupyter nbconvert --clear-output` to fix.')
        return 1
    print('All notebooks are stripped.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
