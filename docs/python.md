Rillgen2D's graphic user interface is built upon Python. 

We use [Anaconda](https://docs.conda.io/en/latest/) `miniconda` to build our environment with all of the necessary dependencies.

### Installing with Conda or mini-Conda

We have provided a `environment.yml` file which can be used with [conda](https://docs.conda.io/en/latest/) to install the stack.

Example install for Linux
```
# update conda
conda update -n base -c defaults conda

# remove old rillgen2d environment
conda remove --name rillgen2d --all

# create new environment for rillgen2d
conda env create -f environment_linux.yml

# activate conda environment
conda activate rillgen2d

# update conda environment 
conda env update --prefix ./env --file environment_linux.yml  --prune
```

To install on Windows, use the environment_windows.yml instead

### Starting the GUI

Once the appropriate Python environment has been created, you can start the GUI

```
# check your python version (should be 3.7.*)
python --version

# start the UI
python rillgen2d.py
```
