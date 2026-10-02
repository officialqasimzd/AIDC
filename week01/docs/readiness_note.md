# Readiness note

Record anything that did not work, exactly as it happened. An honest incomplete
attempt is more useful evidence than copied output, and there is no penalty for
a setup or platform-access problem.

## Toolchain

| Tool | Working? | Version, or the error |
| --- | --- | --- |
| Python 3 | Partly | Python 3.11.1 |
| pandas and NumPy | Yes | pandas 2.3.3; NumPy 2.4.6 |
| VS Code, with the Python and Jupyter extensions | Yes | VS Code 1.139.1. `ms-python.python` and `ms-toolsai.jupyter` are installed. |
| Git and a GitHub account | Yes | Git 2.55.0.windows.5. The repository has the GitHub remote `https://github.com/drmshoaib/AIDC.git`. |
| pytest | Yes | pytest 8.4.2; `6 passed in 1.18s`. The global `py` interpreter does not have pytest installed. |

## Anything that failed

For each failure give the exact command and the full error message.

- **Command:**
- `python --version`
- **Error:** `python : The term 'python' is not recognized as the name of a cmdlet, function, script file, or operable program.`

- **Command:** `py -c "import pandas, numpy; print('pandas', pandas.__version__); print('numpy', numpy.__version__)"`
- **Error:** `ModuleNotFoundError: No module named 'pandas' was debugged further` 

- **Command:** `py -m pytest --version`
- **Error:** `No module named pytest`

## Test run

- **Command:** `week01/.venv/Scripts/python.exe -m pytest`
- **Result:** 6 tests collected.

## Git evidence

- **Latest commit hash:** `0840b355a71d05114c7614624f08309678cb3d22`
- **Pushed to the remote?** yes
- **If no, the access limitation was:**
