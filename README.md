# Overview

[![DOI](https://zenodo.org/badge/834042284.svg)](https://zenodo.org/doi/10.5281/zenodo.13294303)

This repository contains the **"ground truth"** dataset of the Minimum Information about a Tailoring Enzyme (MITE) data repository (`mite_data/data`).

Furthermore, the repository contains auxiliary files and scripts to automatically update them:

- Metadata files summarizing information of all MITE entries in a single file (`mite_data/metadata`)
- Protein FASTA-files for all active (i.e. non-retired) MITE entries and an accompanying up-to-date BLAST database (`mite_data/fasta` and `mite_data/blast_lib`)
- Alphafold-predicted enzyme structures and accompanying image files (`mite_data/pdb` and `mite_data/img`)

When new data is added, auxiliary files must be updated too. Existing fasta and image files will not be overwritten.

For more information, see the README of the [MITE-Standard organisation page](https://github.com/mite-standard).

## Installation (for automated file updates)

*Nota bene*: This installation will only work on (Ubuntu) Linux.

- Install `python 3.12.x`
- Install hatch (e.g. with `pipx install hatch`)
- `hatch env create`
- `sudo snap install pymol-oss` (required for option `--update_img`)
- `sudo apt install ncbi-blast+` (required for option `--update_blast`)

## Quick-start

Update MITE files to the newest version of `mite_schema`: `mite_data --update_mite`

Update only enzyme visualization (re-downloads all AlphaFold PDBs): `mite_data --update_img`.
Note that this module will fail if you have not installed PyMol-OSS.

Update only BLAST database (re-downloads all protein FASTA files): `mite_data --update_blast`

Update all files in repository: `mite_data --update_all`

## Clean-up

If necessary, remove the environment again with `hatch env remove`