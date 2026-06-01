# Readme: Installation Guide and Resources
This guide provides a brief overview of the steps required to set up Python on your machine and implement code efficiently for the problem sets. Of course, there are many different ways to prepare your local setup, and you might already have found your preferred approach.

## Installation Guide
### 1. Download Python distribution with Anaconda
Download the Anaconda Python distribution from [https://www.anaconda.com/download](https://www.anaconda.com/download). Follow the installation instructions.

### 2. Set up an environment and install packages
In contrast to MATLAB or Stata, Python is a programming language developed to execute any computational task. Therefore, the basic Python distribution has only a few functionalities, and to use it for our purposes, we need to install packages, i.e. specialized libraries for each task. The most common packages for our purposes are:
- `numpy` (numeric computations)
- `scipy` (scientific methods, e.g., optimization)
- `statsmodels` (regressions)
- `linearmodels` (panel data and IV regressions)
- `pandas` (data wrangling)
- `matplotlib` (plotting)
- `jupyterlab` (Jupyter notebooks)

As packages are constantly evolving and new versions are released, it is good practice to set up a so-called environment for a project and only install the packages you need for the specific project. This ensures stability of your project code.

**Option A – One-step setup using the provided `environment.yml` (recommended)**

An `environment.yml` file is included in this repository. It specifies all required packages and their versions. To create the environment from it, navigate in the shell/terminal to the directory that includes the .yml, and run:

```bash
conda env create -f environment.yml
conda activate aae2026
```

That's it — skip to step 3.

**Option B – Manual setup via the shell**

If you prefer to build the environment yourself, or need to add packages, follow these steps. Getting comfortable with the shell is worthwhile if you plan to do any programming in research or your career.

1. **Initialize conda in your shell** after installing Anaconda:
   - **Windows**: Use the Anaconda Prompt, or configure the native PowerShell ([instructions](https://stackoverflow.com/questions/64149680/how-can-i-activate-a-conda-environment-from-powershell)).
   - **Mac / Linux**: Works out of the box.

2. **Create an empty environment** (replace `env-name` with your own choice):
   ```bash
   conda create --name env-name python=3.11
   ```

3. **Activate the environment:**
   ```bash
   conda activate env-name
   ```

4. **Install packages.** Most packages are available via conda:
   ```bash
   conda install numpy scipy statsmodels pandas matplotlib jupyterlab -c conda-forge
   ```
   `linearmodels` is not on the default conda channel — install it via pip:
   ```bash
   pip install linearmodels
   ```
   > **Note on conda vs pip:** `conda` and `pip` are both package installers. Prefer `conda` when possible; use `pip` for packages not available on conda channels. Avoid mixing them heavily in the same environment.

5. **Verify the installation:**
   ```bash
   conda list
   ```

**Useful conda commands:**
- List all environments: `conda env list`
- Deactivate current environment: `conda deactivate`
- Export your environment: `conda env export > environment.yml`
- Remove an environment (and all its dependencies): `conda remove --name env-name --all`

More details on environments: [Anaconda docs](https://www.anaconda.com/docs/getting-started/working-with-conda/environments).


### 3. Visual Studio Code (or other IDEs)
With an installed environment, we are ready to execute code. You can develop code in a simple text editor, but there are many better ways to do so. The most widely used integrated development environment (IDE) is Visual Studio Code (VS Code), developed by Microsoft.

**Setup steps:**
1. Download and install [VS Code](https://code.visualstudio.com/).
2. Install the **Python extension** (by Microsoft) from the Extensions panel (`Ctrl+Shift+X`).
3. Install the **Jupyter extension** (by Microsoft) to run notebooks inside VS Code.
4. Open your **project folder** (`File > Open Folder`) — always open the folder, not individual files.
5. Select your conda environment as the Python interpreter: `Ctrl+Shift+P` → *Python: Select Interpreter* → choose `aae2026` (or your env name).

IDEs also offer code formatters, debuggers, and GitHub Copilot. GitHub provides a [free education account](https://education.github.com/pack) with Copilot access — useful (although less so with the recent changes to token and model availability), but always verify AI-generated code carefully, as errors in numerical methods can be subtle.


### 4. Running Code: Scripts vs. Notebooks

There are two main ways to run Python code:

- **`.py` scripts**: Plain Python files, run from the shell (`python script.py`) or via the VS Code run button. Good for reusable functions, data cleaning pipelines, and final estimation code.
- **Jupyter notebooks (`.ipynb`)**: Interactive documents mixing code, output, and text. Well-suited for exploration, visualization, and problem sets. Launch from the shell with:
  ```bash
  jupyter lab
  ```
  Or open a `.ipynb` file directly in VS Code.

**For this course:** We will generally use notebooks for the solutions of the problem sets. Please hand in your solutions to the graded assignments using the provide notebook templates.  


## Resources – Introduction to Python

**Getting started:**
- [QuantEcon – Python Programming](https://python-programming.quantecon.org/intro.html): Good introduction with an economics focus.
- [DataCamp](https://app.datacamp.com): Interactive courses. Some are free with a university email. You can also join the course classroom for additional free access — email mschaller@diw.de.
  - [Intro to Python for Data Science](https://app.datacamp.com/learn/courses/intro-to-python-for-data-science)
  - [Introduction to NumPy](https://app.datacamp.com/learn/courses/introduction-to-numpy)

**Advanced / economics-specific:**
- [QuantEcon Lectures](https://quantecon.org/lectures/): Covers dynamic programming, heterogeneous agents, and more.
- [OpenSourceEconomics](https://github.com/OpenSourceEconomics): Packages for structural economic modeling.
- [Econ-ARK / HARK](https://econ-ark.org/): Toolkit for heterogeneous-agent models.
- [JAX for HPC computing](https://www.youtube.com/watch?v=SstuvS-tVc0): Useful once you need GPU-accelerated or JIT-compiled numerical code.

**Day-to-day problem solving:**
Stack Overflow covers the vast majority of practical Python questions. These days, AI coding assistants (Copilot, Claude, etc.) are likely even more effective — but verify all generated numerical code against known test cases before trusting results.
