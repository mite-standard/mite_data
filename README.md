# Overview

This repository contains entries following the MITE data standard.

Furthermore, it provides functionality to generate images of the characterized enzymes, with structures predicted by AlphaFold.

For more information, see the README of the [organisation page ](https://github.com/mite-standard).

## Installation (for image-generation)

### with `conda` from GitHub

- `conda create --name mite_data python=3.10`
- `conda activate mite_data`
- `conda install -c conda-forge -c schrodinger pymol-bundle`
- `pip install alphafetcher`

## Quick-start

- `python main.py`

This will create/update all protein image