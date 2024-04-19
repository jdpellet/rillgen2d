### Installing with Anaconda (miniconda)

`rillgen2d' graphic user interface (GUI) is built in Python with Streamlit. 

We use [Anaconda](https://docs.conda.io/en/latest/){target=_blank} with [miniconda](https://docs.anaconda.com/free/miniconda/index.html){target=_blank} to build our environment with all of the necessary dependencies. We recommend using the [`mamba`](https://github.com/mamba-org/mamba){target=_blank} solver for faster installation over `conda`.

We have provided three `environment.yml` files which can be used with [conda](https://docs.conda.io/en/latest/){target=_blank} to install Python environment on Linux (Ubuntu), Mac OS X, or Windows 10.

Example install using `conda` and `mamba`:

```bash
# update conda
conda update -n base -c defaults conda

# create new environment for rillgen2d
mamba env create -f environment_linux.yml

# activate conda environment
conda activate rillgen2d
```

to remove or update:

```bash
# check your python version (should be 3.11.*)
python --version

# remove old rillgen2d environment
conda remove --name rillgen2d --all

# update conda environment 
mamba env update --prefix ./env --file environment_linux.yml  --prune
```

### Starting the GUI

Once the `rillgen2d` Python environment has been created, you can start the Streamlit GUI:

```
# start the Streamlit UI
python run.py
```
