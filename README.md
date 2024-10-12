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

Update all files in repository: `mite_data --update_all`

Update only metadata: `mite_data --update_md`

Update only enzyme visualization (re-download all AlphaFold PDBs): `mite_data --update_img`

Update only BLAST database (re-download all protein FASTA files): `mite_data --update_blast`

Update only MITE files to the newest version of `mite_schema`: `mite_data --update_mite`

## Clean-up

If necessary, remove the environment again with `hatch env remove`