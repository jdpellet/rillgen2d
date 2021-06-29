[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip) [![license](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://opensource.org/licenses/GPL-3.0) [![DOI](https://zenodo.org/badge/116533015.svg)](https://zenodo.org/badge/latestdoi/116533015)
# rillgen2d

Code, example data, and manuscript supplemental materials which accompany **Pelletier, JD, XXX**

Lead Author: [Jon D Pelletier](http://jdpellet.github.io/) [![](https://orcid.org/sites/default/files/images/orcid_16x16.png)](http://orcid.org/0000-0002-0702-2646)

Co-Authors: [Jacob van der Leeuw](https://jvanderleeuw) [![](https://orcid.org/sites/default/files/images/orcid_16x16.png)](http://orcid.org/0000-0003-0892-9837),  [Tyson Lee Swetnam](https://tyson-swetnam.github.io/) [![](https://orcid.org/sites/default/files/images/orcid_16x16.png)](http://orcid.org/0000-0002-6639-7181)

## Contents

The repository is organized (in the attempt) to enable reproducible research as part of the [FAIR data principles](https://www.go-fair.org/fair-principles/).

You can (re)run these analyses using your own computer, on commercial cloud, or a data science workbench [CyVerse](https://cyverse.org) Discovery Environment.

## Install and run from command line

### Clone Repository

Clone the repo to your local or VM:

With `git` 
```
git clone https://github.com/jdpellet/rillgen2d
git switch main
```

With GitHub CLI:
```
gh repo clone jdpellet/rillgen2d
```

### Installing with `conda` or `miniconda`

We have provided a `environment.yml` file which can be used with [Conda](https://docs.conda.io/en/latest/) to install the stack.

Example install for Linux command line:

```
# update conda
conda update -n base -c defaults conda

# update conda environments 
conda env update --prefix ./env --file environment.yml  --prune

# or remove old rillgen2d environment
conda remove --name rillgen2d --all

# (re)create environment for rillgen2d
conda env create -f environment_linux.yml

# activate conda environment
conda activate rillgen2d
```