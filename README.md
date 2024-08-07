# Overview

This repository contains entries following the MITE data standard.

Furthermore, it provides functionality to generate images of the characterized enzymes, with structures predicted by AlphaFold.

For more information, see the README of the [organisation page ](https://github.com/mite-standard).

## Installation (for image-generation)

### with `conda` from GitHub

- `pip install alphafetcher`
- `sudo snap install pymol-oss`

## Quick-start

- Download the enzyme pdbs from AlphaFoldDB: `python main.py`
- Generate png images with PyMol: `./generate_png.sh`

This will create all protein images