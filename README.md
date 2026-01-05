# CO3095 Stock Control System — Comprehensive README (Charles Wilson Laboratory)

Repository: https://github.com/ao311-lei/CO3095StockControl.git

This README explains **how to**:
1) download/uncompress the project on a University lab PC (Charles Wilson Laboratory),
2) import it into an IDE,
3) compile/run the program,
4) run **all** test cases, and
5) generate coverage results.

> **Note:** This is a Python project (GitHub shows Python as the repository language). The “compile” step for Python means “set up the environment + run the interpreter”.

---

## 1) Requirements
- **Python 3.10+** (3.11 is also fine)
- Internet access (only needed to install packages if required)

### Optional but recommended
- **VS Code** (with Python extension) or **PyCharm**
- **Git** (only needed if you want to `git clone` instead of downloading a ZIP)

---

## 2) Getting the Project onto the Lab PC

You can do this in **either** of two ways:

### Option A — Download ZIP + Uncompress (easiest)
1. Open the repo page in a browser:
   - https://github.com/ao311-lei/CO3095StockControl
2. Click **Code** → **Download ZIP**
3. Save it somewhere you can find easily (e.g. `Documents`)
4. Right-click the `.zip` file → **Extract All…**
5. Choose a folder location (e.g. `Documents\CO3095StockControl`) → **Extract**

After extraction you should see files like:
- `main.py`
- `src/` (folder)
- `README.md` (this file, or your updated version)

### Option B — Clone using Git (cleanest)
1. Open **Command Prompt** (or PowerShell)
2. Choose a folder (example below uses Documents):
   ```bash
   cd %USERPROFILE%\Documents
