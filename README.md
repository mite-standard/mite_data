# Overview

[![DOI](https://zenodo.org/badge/834042284.svg)](https://zenodo.org/doi/10.5281/zenodo.13294303)

This repository contains the "ground truth" dataset of the Minimum Information about a Tailoring Enzyme (MITE) data repository (`mite_data/data`).

Furthermore, the repository provides functionality to generate metadata, create protein visualizations, and generate a BLAST database of the entries.

For more information, see the README of the [MITE-Standard organisation page](https://github.com/mite-standard).

## Installation (for image-generation)

*Nota bene*: This installation will only work on (Ubuntu) Linux.

- `hatch env create`
- `sudo snap install pymol-oss` (required for option `--update_img`)
- `sudo apt install ncbi-blast+` (required for option `--update_blast`)

## Quick-start

Update all files in repository: `mite_data --update_all`

Update only enzyme visualization (re-downloads all AlphaFold PDBs): `mite_data --update_img`.
Note that this module will fail if you have not installed PyMol-OSS.

Update only BLAST database (re-downloads all protein FASTA files): `mite_data --update_blast`

Update only MITE files to the newest version of `mite_schema`: `mite_data --update_mite`

## Clean-up

If necessary, remove the environment again with `hatch env remove`