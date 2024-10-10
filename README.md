# Overview

[![DOI](https://zenodo.org/badge/834042284.svg)](https://zenodo.org/doi/10.5281/zenodo.13294303)

This repository contains entries following the MITE data standard (`data`).

Furthermore, it provides functionality to generate images of the characterized enzymes, with structures predicted by AlphaFold.

For more information, see the README of the [MITE-Standard organisation page](https://github.com/mite-standard).

## Installation (for image-generation)

*Nota bene*: This installation will only work on (Ubuntu) Linux.

- `hatch env create`
- `sudo snap install pymol-oss`

## Quick-start

TBA - Change here


- Download the enzyme pdbs from AlphaFoldDB: `hatch run python mite_data/main.py`
- Generate png images with PyMol: `./generate_png.sh`

This will create all protein images
